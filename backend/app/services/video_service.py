"""
Video Rendering Service
Composites audio, graphics, and presenter video into final output using FFmpeg.
"""
import os
import uuid
import logging
import subprocess
import re
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

    def _find_font(self) -> str:
        """Find a usable TrueType font. Returns path or empty string."""
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        for font in candidates:
            if os.path.exists(font):
                return font
        logger.warning("No TrueType font found, captions will use FFmpeg default")
        return ""

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
        scenes: Optional[List[Dict[str, Any]]] = None,
        sentiment: str = "stable"
    ) -> Dict[str, Any]:
        """
        Render a professional YouTube-quality short clip with:
        - Multi-scene Documentary Style
        - Scene-specific images and overlays
        - Sentiment-based color grading
        - Ken Burns effect on B-roll images
        - Dark gradient overlay for text readability
        - Headline title card (first 3 seconds)
        - Snappy 2-3 word captions with keyword highlighting
        - Animated progress bar
        - Branding watermark
        """
        if not self._check_ffmpeg():
            return {"error": "FFmpeg not available"}

        filename = f"short_{uuid.uuid4().hex[:12]}.mp4"
        output_path = os.path.join(self.short_clip_dir, filename)

        # 0. Style and Timing
        style = profile.get("video_style", {}) if profile else {}
        bg_color = style.get("backgroundColor", background_color)
        txt_color = style.get("textColor", text_color)
        duration = self._get_media_duration(audio_path)
        if duration <= 0: duration = 30
        
        # 1. Prepare Scenes and Normalization
        if not scenes:
            scenes = [{"voiceover": script_text or headline, "duration_seconds": duration, "overlay_text": headline}]
        
        # Normalize scene durations to actual audio length
        total_requested = sum(s.get("duration_seconds", 5) for s in scenes)
        
        # 2. Build Video Filter (Images with Ken Burns)
        video_filters = []
        inputs = []
        font_path = self._find_font()
        font_spec = f":fontfile='{font_path}'" if font_path else ""
        
        for i, scene in enumerate(scenes):
            # Pick image for this scene (looping if needed)
            img_idx = i % len(image_paths) if image_paths else -1
            img = image_paths[img_idx] if img_idx >= 0 else None
            
            # Scene timing
            scene_raw_dur = scene.get("duration_seconds", 5)
            scene_duration = (scene_raw_dur / total_requested) * duration
            
            if img:
                inputs.extend(["-loop", "1", "-t", f"{scene_duration:.2f}", "-i", img])
                # Ken Burns effect specific to scene
                zoom_dir = "min(zoom+0.001,1.3)" if i % 2 == 0 else "if(eq(on,1),1.3,max(zoom-0.001,1.0))"
                video_filters.append(
                    f"[{i}:v]scale=2160:-1,crop=1080:1920,"
                    f"zoompan=z='{zoom_dir}':d={int(scene_duration*30)}:s=1080x1920"
                    f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps=30[v{i}]"
                )
            else:
                inputs.extend(["-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:d={scene_duration:.2f}:r=30"])
                video_filters.append(f"[{i}:v]null[v{i}]")

        # Concatenate scene clips
        concat_filter = "".join([f"[v{i}]" for i in range(len(scenes))])
        video_filters.append(f"{concat_filter}concat=n={len(scenes)}:v=1:a=0[rawbg]")

        # 3. Sentiment-based Color Grading
        color_grading = "null"
        if sentiment == "tense":
            # Desaturate and blue-ish tint
            color_grading = "eq=saturation=0.7:brightness=-0.05,colorbalance=bt=0.05:mt=0.05"
        elif sentiment == "hopeful":
            # Warm and vibrant
            color_grading = "eq=saturation=1.2:brightness=0.02,colorbalance=rt=0.05:gt=0.02"

        video_filters.append(f"[rawbg]{color_grading}[gradedbg]")

        # 4. Overlays (Gradient + Text)
        video_filters.append(
            f"[gradedbg]drawbox=x=0:y=ih*0.4:w=iw:h=ih*0.6:color=black@0.55:t=fill,"
            f"drawbox=x=0:y=0:w=iw:h=ih*0.15:color=black@0.5:t=fill[bgv]"
        )

        overlay_filters = []
        title_duration = min(3.0, duration * 0.1)
        
        # ── Title Card (only for first scene) ──
        safe_headline = re.sub(r"['\";\\()\[\]{}]", "", headline[:50]).replace(":", "\\:").replace(",", "\\,").replace("%", "%%")
        overlay_filters.append(
            f"drawtext=text='INTELLIGENCE REPORT':fontcolor=#C7A84A:fontsize=32{font_spec}"
            f":x=(w-text_w)/2:y=250:borderw=2:bordercolor=black:enable='between(t,0,{title_duration})',"
            f"drawtext=text='{safe_headline}':fontcolor=white:fontsize=56{font_spec}"
            f":x=(w-text_w)/2:y=(h/2)-60:borderw=3:bordercolor=black"
            f":shadowcolor=black@0.8:shadowx=4:shadowy=4:enable='between(t,0,{title_duration})'"
        )

        # ── Per-Scene Overlays & Captions ──
        current_time = 3.0 # Start after title
        for i, scene in enumerate(scenes):
            scene_dur = (scene.get("duration_seconds", 5) / total_requested) * duration
            start = current_time
            end = current_time + scene_dur
            current_time = end

            # Scene Overlay Text (Middle-top headline)
            scene_text = scene.get("overlay_text", "").upper()
            if scene_text:
                safe_scene_text = re.sub(r"['\";\\()\[\]{}]", "", scene_text).replace(":", "\\:").replace(",", "\\,")
                overlay_filters.append(
                    f"drawtext=text='{safe_scene_text}':fontcolor=#FFD700:fontsize=42{font_spec}"
                    f":x=(w-text_w)/2:y=350:borderw=3:bordercolor=black"
                    f":enable='between(t,{start:.2f},{end:.2f})'"
                )

            # Scene Captions (at bottom)
            voiceover = scene.get("voiceover", "")
            if voiceover:
                caption_f = self._create_caption_filter(voiceover, scene_dur, txt_color, start)
                if caption_f: overlay_filters.append(caption_f)

        # ── Constant Elements ──
        overlay_filters.append(
            # Progress Bar
            f"drawbox=x=0:y=h-8:w=iw:h=8:color=white@0.15:t=fill,"
            f"drawbox=x=0:y=h-8:w='iw*t/{duration:.2f}':h=8:color=#C7A84A:t=fill"
        )
        overlay_filters.append(
            # Branding
            f"drawtext=text='@StrategicContext':fontcolor=white@0.85:fontsize=28{font_spec}:x=(w-text_w)/2:y=h-60:box=1:boxcolor=black@0.5:boxborderw=8"
        )
        overlay_filters.append(
            # Badge
            f"drawtext=text='LIVE':fontcolor=white:fontsize=24{font_spec}:x=50:y=50:box=1:boxcolor=red@0.8:boxborderw=10"
        )

        # Final Glitch Effect (last 0.5s)
        overlay_filters.append(
            f"noise=alls=20:allf=t+u:enable='between(t,{duration-0.5:.2f},{duration:.2f})'"
        )

        # 5. FFmpeg Command Construction
        all_overlays_str = ",".join(overlay_filters)
        # Ensure there is a semicolon before the overlay chain if it's separate, 
        # or just chain them if bgv is the last filter's output.
        full_video_filter = ";".join(video_filters) + f";[bgv]{all_overlays_str}[out_v]"

        # 4. Audio Mixing (TTS + Background Music)
        # The audio input index will be after all image/color inputs.
        # Each scene potentially adds one video input.
        # So, the audio_path input index is len(scenes).
        audio_input_idx = len(scenes) 
        inputs.extend(["-i", audio_path])
        
        mix_filter = f";[{audio_input_idx}:a]volume=1.0[main_a]"
        if music_path and os.path.exists(music_path):
            music_idx = audio_input_idx + 1 # Music input comes after the main audio input
            inputs.extend(["-stream_loop", "-1", "-i", music_path])
            mix_filter += f";[{music_idx}:a]volume=0.12,apad[bg_a]; [main_a][bg_a]amix=inputs=2:duration=first[out_a]"
        else:
            mix_filter += f";[main_a]anull[out_a]"

        # Full FFmpeg Command
        cmd = [
            "ffmpeg", "-y",
        ] + inputs + [
            "-filter_complex", 
            f"{full_video_filter}{mix_filter}",
            "-map", "[out_v]",
            "-map", "[out_a]",
            "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            output_path,
        ]

        logger.info(f"Running FFmpeg: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"FFmpeg failed with return code {result.returncode}")
                logger.error(f"FFmpeg command: {' '.join(cmd)}")
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

    def _create_caption_filter(self, text: str, total_duration: float, color: str, start_offset: float = 0.0) -> str:
        """Create professional snappy caption filters with keyword highlighting."""
        import re

        # Split text into snappy 2-3 word phrases
        words = text.split()
        phrases = []
        current_phrase = []
        for word in words:
            current_phrase.append(word)
            if len(current_phrase) >= 3 or word.endswith(('.', ',', '!', '?')):
                phrases.append(" ".join(current_phrase))
                current_phrase = []
        if current_phrase:
            phrases.append(" ".join(current_phrase))
            
        if not phrases:
            return ""

        # Captions start after the title card
        caption_duration = total_duration - start_offset
        if caption_duration <= 0:
            caption_duration = total_duration
            start_offset = 0
            
        filters = []
        font_path = self._find_font()
        font_spec = f":fontfile='{font_path}'" if font_path else ""
        
        # Impact keywords for yellow highlighting
        highlight_keywords = {
            "conflict", "surge", "ceasefire", "attack", "crisis", "war",
            "strike", "escalation", "missile", "rebel", "military",
            "agreement", "deal", "threat", "sanctions", "nuclear",
            "troops", "invasion", "bombing", "killed", "tension"
        }

        # Calculate character density for perfect audio sync
        total_weight = sum(len(p) + 4 for p in phrases) # +4 base weight per phrase
        current_time = start_offset

        for i, phrase in enumerate(phrases):
            phrase_weight = len(phrase) + 4
            phrase_duration = caption_duration * (phrase_weight / total_weight)
            
            start = current_time
            end = current_time + phrase_duration
            current_time = end

            # Dynamic color highlighting
            phrase_lower = phrase.lower()
            is_highlighted = any(k in phrase_lower for k in highlight_keywords)
            dynamic_color = "#FFD700" if is_highlighted else color

            # Sanitize text for FFmpeg drawtext
            safe_phrase = re.sub(r"['\";\\()\[\]{}]", "", phrase)
            safe_phrase = safe_phrase.replace(":", "\\:")
            safe_phrase = safe_phrase.replace("%", "%%")
            safe_phrase = safe_phrase.replace(",", "\\,")

            # Dynamic font scaling to prevent overflow
            font_size = 80 if is_highlighted else 72
            if len(safe_phrase) > 20:
                font_size = 50
            elif len(safe_phrase) > 15:
                font_size = 60

            filters.append(
                f"drawtext=text='{safe_phrase}':fontcolor={dynamic_color}:fontsize={font_size}{font_spec}"
                f":x=(w-text_w)/2:y=(h*0.65)"
                f":borderw=5:bordercolor=black"
                f":shadowcolor=black@0.9:shadowx=4:shadowy=4"
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
