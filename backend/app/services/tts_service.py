"""
Text-to-Speech Service
Multi-engine TTS: Edge-TTS (free, high quality) | ElevenLabs (paid) | Piper (offline) | gTTS (fallback)
"""
import os
import uuid
import logging
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Multi-engine Text-to-Speech service."""

    def __init__(self):
        self.engine = settings.TTS_ENGINE  # "edge_tts", "elevenlabs", "piper", or "gtts"
        self.api_key = settings.ELEVENLABS_API_KEY
        self.edge_voice = getattr(settings, "EDGE_TTS_VOICE", "en-US-GuyNeural")
        self.piper_model = getattr(settings, "PIPER_TTS_MODEL", "en_US-lessac-medium")
        self.output_dir = os.path.join(settings.VIDEO_OUTPUT_DIR, "audio")
        os.makedirs(self.output_dir, exist_ok=True)

    def reload_settings(self):
        """Reload TTS settings from config (called when admin changes settings)."""
        self.engine = settings.TTS_ENGINE
        self.api_key = settings.ELEVENLABS_API_KEY
        self.edge_voice = getattr(settings, "EDGE_TTS_VOICE", "en-US-GuyNeural")
        self.piper_model = getattr(settings, "PIPER_TTS_MODEL", "en_US-lessac-medium")

    async def generate_audio(
        self,
        text: str,
        voice_id: str = "default",
        filename: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate audio from text. Supports overrides from a Profile persona.
        """
        if not filename:
            filename = f"{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(self.output_dir, filename)

        # Profile Overrides
        engine = profile.get("voice_engine", self.engine) if profile else self.engine
        voice = profile.get("voice_id", voice_id) if profile else voice_id

        # Engine priority
        if engine == "elevenlabs" and self.api_key:
            return await self._elevenlabs_generate(text, voice, output_path)
        elif engine == "edge_tts":
            return await self._edge_tts_generate(text, voice, output_path)
        elif engine == "piper":
            return await self._piper_tts_generate(text, output_path)
        else:
            return await self._gtts_fallback(text, output_path)

    # ─────────────────────────────────────────────
    # ENGINE: Edge-TTS (Free, Cloud, High Quality)
    # ─────────────────────────────────────────────
    async def _edge_tts_generate(
        self, text: str, voice_id: str, output_path: str
    ) -> Dict[str, Any]:
        """Generate audio using Microsoft Edge TTS (free, no API key)."""
        try:
            import edge_tts

            # Use specified voice or fall back to config default
            voice = voice_id if voice_id != "default" else self.edge_voice

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

            file_size = os.path.getsize(output_path)
            duration = await self._get_audio_duration(output_path)

            logger.info(f"Edge-TTS audio generated: {output_path} ({duration}s, voice={voice})")
            return {
                "path": output_path,
                "url": f"/output/audio/{os.path.basename(output_path)}",
                "duration_seconds": duration,
                "file_size": file_size,
                "engine": "edge_tts",
                "voice": voice,
            }
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            return await self._gtts_fallback(text, output_path)
        except Exception as e:
            logger.error(f"Edge-TTS generation failed: {e}, falling back to gTTS")
            return await self._gtts_fallback(text, output_path)

    # ─────────────────────────────────────────────
    # ENGINE: Piper TTS (Free, Offline, Local)
    # ─────────────────────────────────────────────
    async def _piper_tts_generate(
        self, text: str, output_path: str
    ) -> Dict[str, Any]:
        """Generate audio using Piper TTS (offline, local)."""
        try:
            import subprocess
            import wave
            import io

            # Piper outputs WAV, we'll convert to MP3
            wav_path = output_path.replace(".mp3", ".wav")

            # Use piper CLI which auto-downloads models
            cmd = [
                "piper",
                "--model", self.piper_model,
                "--output_file", wav_path,
            ]

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate(input=text.encode("utf-8"))

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {stderr.decode()}")
                return await self._gtts_fallback(text, output_path)

            # Convert WAV to MP3 using ffmpeg
            mp3_cmd = [
                "ffmpeg", "-y", "-i", wav_path,
                "-codec:a", "libmp3lame", "-b:a", "192k",
                output_path,
            ]
            subprocess.run(mp3_cmd, capture_output=True)

            # Clean up WAV
            if os.path.exists(wav_path):
                os.remove(wav_path)

            file_size = os.path.getsize(output_path)
            duration = await self._get_audio_duration(output_path)

            logger.info(f"Piper TTS audio generated: {output_path} ({duration}s)")
            return {
                "path": output_path,
                "url": f"/output/audio/{os.path.basename(output_path)}",
                "duration_seconds": duration,
                "file_size": file_size,
                "engine": "piper",
            }
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}, falling back to gTTS")
            return await self._gtts_fallback(text, output_path)

    # ─────────────────────────────────────────────
    # ENGINE: ElevenLabs (Paid, Premium Quality)
    # ─────────────────────────────────────────────
    async def _elevenlabs_generate(
        self, text: str, voice_id: str, output_path: str
    ) -> Dict[str, Any]:
        """Generate audio using ElevenLabs API."""
        import httpx

        if voice_id == "default":
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(response.content)

                file_size = os.path.getsize(output_path)
                duration = await self._get_audio_duration(output_path)

                logger.info(f"ElevenLabs audio generated: {output_path} ({duration}s)")
                return {
                    "path": output_path,
                    "url": f"/output/audio/{os.path.basename(output_path)}",
                    "duration_seconds": duration,
                    "file_size": file_size,
                    "engine": "elevenlabs",
                }
        except Exception as e:
            logger.error(f"ElevenLabs failed: {e}, falling back to Edge-TTS")
            return await self._edge_tts_generate(text, "default", output_path)

    # ─────────────────────────────────────────────
    # ENGINE: gTTS (Free, Basic, Emergency Fallback)
    # ─────────────────────────────────────────────
    async def _gtts_fallback(self, text: str, output_path: str) -> Dict[str, Any]:
        """Fallback: Generate audio using Google TTS (free, lower quality)."""
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)

            file_size = os.path.getsize(output_path)
            duration = await self._get_audio_duration(output_path)

            logger.info(f"gTTS audio generated: {output_path} ({duration}s)")
            return {
                "path": output_path,
                "url": f"/output/audio/{os.path.basename(output_path)}",
                "duration_seconds": duration,
                "file_size": file_size,
                "engine": "gtts",
            }
        except ImportError:
            logger.error("gTTS not installed. Run: pip install gTTS")
            return {"error": "No TTS engine available. Install gTTS or edge-tts."}
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            return {"error": str(e)}

    # ─────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────
    async def _get_audio_duration(self, file_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path)
            return round(len(audio) / 1000.0, 2)
        except ImportError:
            file_size = os.path.getsize(file_path)
            return round(file_size / (128 * 1024 / 8), 2)
        except Exception:
            return 0.0

    async def generate_segment_audios(
        self, segments: list, voice_id: str = "default", profile: Optional[Dict[str, Any]] = None
    ) -> list:
        """Generate audio for each script segment."""
        results = []
        for i, segment in enumerate(segments):
            content = segment.get("content", "")
            if not content:
                continue
            filename = f"segment_{i}_{uuid.uuid4().hex[:8]}.mp3"
            result = await self.generate_audio(content, voice_id, filename, profile=profile)
            result["segment_index"] = i
            result["segment_type"] = segment.get("type", "unknown")
            results.append(result)
        return results

    def get_available_voices(self) -> list:
        """Return list of available TTS voices based on current engine."""
        if self.engine == "elevenlabs" and self.api_key:
            return [
                {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (Female)", "accent": "American"},
                {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi (Female)", "accent": "American"},
                {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella (Female)", "accent": "American"},
                {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni (Male)", "accent": "American"},
                {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli (Female)", "accent": "American"},
                {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh (Male)", "accent": "American"},
                {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold (Male)", "accent": "American"},
                {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam (Male)", "accent": "American"},
                {"id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam (Male)", "accent": "American"},
            ]
        elif self.engine == "edge_tts":
            return [
                {"id": "en-US-GuyNeural", "name": "Guy (Male, Deep)", "accent": "American", "recommended": True},
                {"id": "en-US-JennyNeural", "name": "Jenny (Female, Clear)", "accent": "American"},
                {"id": "en-US-AriaNeural", "name": "Aria (Female, Warm)", "accent": "American"},
                {"id": "en-US-DavisNeural", "name": "Davis (Male, Calm)", "accent": "American"},
                {"id": "en-GB-RyanNeural", "name": "Ryan (Male, BBC-Style)", "accent": "British"},
                {"id": "en-GB-SoniaNeural", "name": "Sonia (Female)", "accent": "British"},
                {"id": "en-AU-WilliamNeural", "name": "William (Male)", "accent": "Australian"},
                {"id": "en-IN-PrabhatNeural", "name": "Prabhat (Male)", "accent": "Indian"},
                {"id": "en-IN-NeerjaNeural", "name": "Neerja (Female)", "accent": "Indian"},
                {"id": "hi-IN-MadhurNeural", "name": "Madhur (Male, Hindi)", "accent": "Hindi"},
                {"id": "hi-IN-SwaraNeural", "name": "Swara (Female, Hindi)", "accent": "Hindi"},
            ]
        elif self.engine == "piper":
            return [
                {"id": "en_US-lessac-medium", "name": "Lessac (Male, Medium)", "accent": "American"},
                {"id": "en_US-amy-medium", "name": "Amy (Female, Medium)", "accent": "American"},
                {"id": "en_GB-alan-medium", "name": "Alan (Male, Medium)", "accent": "British"},
            ]
        else:
            return [
                {"id": "default", "name": "Google TTS (Default)", "accent": "American"},
            ]


tts_service = TTSService()
