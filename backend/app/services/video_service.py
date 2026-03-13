"""
Video Rendering Service
Composites audio, graphics, and presenter video into final output using FFmpeg.
"""
import os
import uuid
import logging
import subprocess
import json
from typing import Optional, Dict, Any, List

from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoRenderService:
    """Video rendering service using FFmpeg for compositing."""

    def __init__(self):
        self.output_dir = settings.VIDEO_OUTPUT_DIR
        self.short_clip_dir = os.path.join(self.output_dir, "shorts")
        self.presenter_dir = os.path.join(self.output_dir, "presenter")
        self.thumbnail_dir = os.path.join(self.output_dir, "thumbnails")

        for d in [self.output_dir, self.short_clip_dir, self.presenter_dir, self.thumbnail_dir]:
            os.makedirs(d, exist_ok=True)

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg not found. Install it: apt-get install ffmpeg")
            return False

    async def render_short_clip(
        self,
        audio_path: str,
        headline: str,
        script_text: str = "",
        image_paths: List[str] = [],
        background_color: str = "#1a1a2e",
        text_color: str = "white",
        music_path: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Render a high-quality short clip with:
        - Image B-roll (zoom/pan transitions)
        - Dynamic synchronized captions
        - Background music mixing
        """
        if not self._check_ffmpeg():
            return {"error": "FFmpeg not available"}

        filename = f"short_{uuid.uuid4().hex[:12]}.mp4"
        output_path = os.path.join(self.short_clip_dir, filename)

        # 0. Profile Style Overrides
        style = profile.get("video_style", {}) if profile else {}
        bg_color = style.get("backgroundColor", background_color)
        txt_color = style.get("textColor", text_color)

        # 1. Calculate timing
        duration = self._get_media_duration(audio_path)
        if duration <= 0:
            duration = 30

        # 2. Build Video Filter (Images + Zoom/Pan)
        video_filters = []
        inputs = []
        
        if image_paths:
            # Multi-image B-roll with crossfade
            per_image_duration = duration / len(image_paths)
            for i, img in enumerate(image_paths):
                inputs.extend(["-loop", "1", "-t", str(per_image_duration + 1), "-i", img])
                # Ken Burns effect (Subtle zoom)
                video_filters.append(
                    f"[{i}:v]scale=1920:-1,crop=1080:1920,"
                    f"zoompan=z='min(zoom+0.0015,1.5)':d={int((per_image_duration+1)*30)}:s=1080x1920:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v{i}];"
                )
            
            # Concatenate images
            concat_filter = "".join([f"[v{i}]" for i in range(len(image_paths))])
            video_filters.append(f"{concat_filter}concat=n={len(image_paths)}:v=1:a=0[bgv];")
        else:
            # Fallback to solid color
            inputs.extend(["-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:d={duration}:r=30"])
            video_filters.append("[0:v]null[bgv];")

        # 3. Dynamic Captions (Timed text blocks)
        caption_filter_inner = self._create_caption_filter(script_text or headline, duration, txt_color)
        if caption_filter_inner:
            full_video_filter = "".join(video_filters) + f"[bgv]{caption_filter_inner}[out_v];"
        else:
            full_video_filter = "".join(video_filters) + f"[bgv]null[out_v];"

        # 4. Audio Mixing (TTS + Background Music)
        audio_input_idx = len(image_paths) if image_paths else 1
        inputs.extend(["-i", audio_path])
        
        mix_filter = f"[{audio_input_idx}:a]volume=1.0[main_a];"
        if music_path and os.path.exists(music_path):
            music_idx = audio_input_idx + 1
            inputs.extend(["-stream_loop", "-1", "-i", music_path])
            mix_filter += f"[{music_idx}:a]volume=0.15,apad[bg_a]; [main_a][bg_a]amix=inputs=2:duration=first[out_a]"
        else:
            mix_filter += f"[main_a]copy[out_a]"

        # Full FFmpeg Command
        cmd = [
            "ffmpeg", "-y",
        ] + inputs + [
            "-filter_complex", 
            full_video_filter + mix_filter,
            "-map", "[out_v]",
            "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            output_path,
        ]

        logger.info(f"Running FFmpeg: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"FFmpeg failed with return code {result.returncode}")
                logger.error(f"FFmpeg stdout: {result.stdout}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                return {"error": f"FFmpeg rendering failed: {result.stderr[:200]}"}

            return {
                "path": output_path,
                "url": f"/output/shorts/{filename}",
                "duration_seconds": duration,
                "file_size": os.path.getsize(output_path),
                "resolution": "1080x1920",
                "type": "short_clip",
            }
        except Exception as e:
            return {"error": str(e)}

    def _create_caption_filter(self, text: str, total_duration: float, color: str) -> str:
        """Create a series of drawtext filters for timed captions."""
        import re
        
        # Split text into phrases of ~5-7 words
        words = text.split()
        phrases = []
        current_phrase = []
        for word in words:
            current_phrase.append(word)
            if len(current_phrase) >= 6:
                phrases.append(" ".join(current_phrase))
                current_phrase = []
        if current_phrase:
            phrases.append(" ".join(current_phrase))
            
        if not phrases:
            return "null"

        phrase_duration = total_duration / len(phrases)
        filters = []
        
        for i, phrase in enumerate(phrases):
            start = i * phrase_duration
            end = (i + 1) * phrase_duration
            # Escape text for FFmpeg
            safe_phrase = phrase.replace("'", "'\\''").replace(":", "\\:")
            # Wrap lines if too long
            if len(safe_phrase) > 25:
                mid = len(safe_phrase) // 2
                split_idx = safe_phrase.find(" ", mid-5)
                if split_idx != -1:
                    safe_phrase = safe_phrase[:split_idx] + "\\\\n" + safe_phrase[split_idx+1:]

            filters.append(
                f"drawtext=text='{safe_phrase}':fontcolor={color}:fontsize=64:fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'"
                f":x=(w-text_w)/2:y=(h-text_h)/2+200"
                f":borderw=3:bordercolor=black"
                f":enable='between(t,{start:.2f},{end:.2f})'"
            )
            
        return ",".join(filters)


    async def render_presenter_video(
        self,
        audio_path: str,
        avatar_video_path: str,
        headline: str = "",
        lower_third_text: str = "",
    ) -> Dict[str, Any]:
        """
        Render a full presenter video with lip-synced avatar, lower-third graphics, and audio.
        """
        if not self._check_ffmpeg():
            return {"error": "FFmpeg not available"}

        filename = f"presenter_{uuid.uuid4().hex[:12]}.mp4"
        output_path = os.path.join(self.presenter_dir, filename)

        safe_lower_third = lower_third_text.replace("'", "'\\''").replace(":", "\\:")

        # FFmpeg: overlay avatar video + lower-third text + audio
        filter_complex = (
            f"[0:v]scale=1920:1080[bg];"
            f"[bg]drawtext=text='{safe_lower_third}'"
            f":fontcolor=white:fontsize=32"
            f":x=50:y=h-100:font=Arial"
            f":box=1:boxcolor=black@0.7:boxborderw=10[out]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", avatar_video_path,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[out]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            output_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr[:500]}")
                return {"error": f"FFmpeg rendering failed: {result.stderr[:200]}"}

            file_size = os.path.getsize(output_path)
            duration = self._get_media_duration(output_path)

            return {
                "path": output_path,
                "url": f"/output/presenter/{filename}",
                "duration_seconds": duration,
                "file_size": file_size,
                "resolution": "1920x1080",
                "type": "presenter_video",
            }
        except subprocess.TimeoutExpired:
            return {"error": "FFmpeg rendering timed out (10 min limit)"}
        except Exception as e:
            return {"error": str(e)}

    async def create_thumbnail(
        self,
        headline: str,
        background_color: str = "#0f3460",
    ) -> Dict[str, Any]:
        """Create a thumbnail image with text overlay."""
        if not self._check_ffmpeg():
            return {"error": "FFmpeg not available"}

        filename = f"thumb_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(self.thumbnail_dir, filename)
        safe_text = headline[:60].replace("'", "'\\''").replace(":", "\\:")

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={background_color}:s=1280x720:d=1",
            "-vf", (
                f"drawtext=text='{safe_text}'"
                f":fontcolor=white:fontsize=56"
                f":x=(w-text_w)/2:y=(h-text_h)/2"
                f":font=Arial"
            ),
            "-frames:v", "1",
            output_path,
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            return {
                "path": output_path,
                "url": f"/output/thumbnails/{filename}",
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_media_duration(self, file_path: str) -> float:
        """Get media duration using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                file_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
        except Exception:
            return 0.0


video_render_service = VideoRenderService()
