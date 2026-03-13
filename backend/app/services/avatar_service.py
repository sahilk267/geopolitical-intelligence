"""
Avatar / Lip-Sync Service
Generates lip-synced presenter videos using:
  - Local SadTalker (Free, Open-Source, Offline)
  - D-ID API (Paid)
  - HeyGen API (Paid)
"""
import os
import uuid
import asyncio
import logging
import subprocess
import glob
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.http_client import http_client

logger = logging.getLogger(__name__)


class AvatarService:
    """Generates lip-synced presenter videos. Supports local (SadTalker) and cloud APIs."""

    def __init__(self):
        self.engine = getattr(settings, "AVATAR_ENGINE", "local")
        self.did_api_key = getattr(settings, "DID_API_KEY", None)
        self.heygen_api_key = getattr(settings, "HEYGEN_API_KEY", None)
        self.default_presenter = getattr(
            settings, "DEFAULT_PRESENTER_IMAGE", "./assets/presenter.png"
        )
        self.sadtalker_dir = getattr(settings, "SADTALKER_DIR", "../sadtalker")
        self.output_dir = os.path.join(settings.VIDEO_OUTPUT_DIR, "avatars")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_lipsync(
        self,
        audio_url: str,
        presenter_image: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a lip-synced presenter video.
        Returns: { "path": str, "url": str, "duration_seconds": float }
        """
        image = presenter_image or self.default_presenter

        # --- Local SadTalker (Free, Open-Source) ---
        if self.engine == "local":
            return await self._local_generate(audio_url, image)

        # --- Cloud APIs (Paid) ---
        # D-ID/HeyGen require public image URLs
        if (self.engine == "did" and self.did_api_key) or (self.engine == "heygen" and self.heygen_api_key):
            if image.startswith(".") or image.startswith("/") or not image.startswith("http"):
                logger.warning(f"Avatar API requires a public image URL, but got local path: {image}. Skipping.")
                return {
                    "error": "Avatar API requires a public image URL. Please upload your presenter image or use a public URL in Settings.",
                    "fallback": True,
                }

        if self.engine == "did" and self.did_api_key:
            return await self._did_generate(audio_url, image)
        elif self.engine == "heygen" and self.heygen_api_key:
            return await self._heygen_generate(audio_url, image)
        else:
            logger.warning("No avatar engine configured. Attempting local SadTalker fallback.")
            return await self._local_generate(audio_url, image)

    # ─── Local SadTalker Engine (Free, Offline) ───────────────────────────

    async def _local_generate(
        self, audio_path: str, presenter_image: str
    ) -> Dict[str, Any]:
        """Generate a lip-synced video using local SadTalker installation."""
        sadtalker_root = os.path.abspath(self.sadtalker_dir)
        inference_script = os.path.join(sadtalker_root, "inference.py")
        checkpoint_dir = os.path.join(sadtalker_root, "checkpoints")
        venv_python = os.path.join(sadtalker_root, "venv", "Scripts", "python.exe")

        # Validate installation
        if not os.path.exists(inference_script):
            logger.error(f"SadTalker not found at {sadtalker_root}. Please install it.")
            return {
                "error": f"SadTalker not installed at {sadtalker_root}. Run the setup guide.",
                "fallback": True,
            }

        if not os.path.exists(checkpoint_dir):
            logger.error(f"SadTalker checkpoints not found at {checkpoint_dir}.")
            return {
                "error": "SadTalker checkpoints missing. Download them to the checkpoints/ folder.",
                "fallback": True,
            }

        # Determine the Python executable
        python_exe = venv_python if os.path.exists(venv_python) else "python"

        # Resolve paths for the presenter image and audio
        abs_image = os.path.abspath(presenter_image)
        abs_audio = os.path.abspath(audio_path)

        if not os.path.exists(abs_image):
            logger.warning(f"Presenter image not found: {abs_image}. Using SadTalker example.")
            abs_image = os.path.join(sadtalker_root, "examples", "source_image", "full_body_1.png")

        if not os.path.exists(abs_audio):
            logger.error(f"Audio file not found: {abs_audio}")
            return {"error": f"Audio file not found: {abs_audio}"}

        # Output directory for this generation
        result_dir = os.path.join(self.output_dir, f"sadtalker_{uuid.uuid4().hex[:8]}")
        os.makedirs(result_dir, exist_ok=True)

        # Build the SadTalker CLI command
        cmd = [
            python_exe,
            inference_script,
            "--driven_audio", abs_audio,
            "--source_image", abs_image,
            "--checkpoint_dir", checkpoint_dir,
            "--result_dir", result_dir,
            "--size", "256",
            "--preprocess", "crop",
            "--still",
            "--cpu",  # Use CPU for Intel Iris Xe compatibility
        ]

        logger.info(f"SadTalker: starting local generation...")
        logger.debug(f"SadTalker command: {' '.join(cmd)}")

        try:
            # Run as a subprocess (non-blocking)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=sadtalker_root,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600,  # 10 minute timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace")[-500:]
                logger.error(f"SadTalker failed (exit {process.returncode}): {error_msg}")
                return {"error": f"SadTalker generation failed: {error_msg}"}

            # Find the generated video file
            output_pattern = os.path.join(result_dir, "*.mp4")
            # SadTalker also creates <result_dir>.mp4 in the parent
            parent_mp4 = result_dir + ".mp4"

            output_video = None
            if os.path.exists(parent_mp4):
                output_video = parent_mp4
            else:
                mp4_files = glob.glob(output_pattern)
                if mp4_files:
                    output_video = mp4_files[0]

            if not output_video:
                logger.error(f"SadTalker produced no output video in {result_dir}")
                return {"error": "SadTalker produced no output video."}

            # Move to a clean filename
            final_name = f"avatar_{uuid.uuid4().hex[:12]}.mp4"
            final_path = os.path.join(self.output_dir, final_name)
            os.rename(output_video, final_path)

            logger.info(f"SadTalker: generated {final_path}")

            return {
                "path": final_path,
                "url": f"/output/avatars/{final_name}",
                "duration_seconds": 0,  # Can be computed via ffprobe if needed
                "engine": "local_sadtalker",
            }

        except asyncio.TimeoutError:
            logger.error("SadTalker generation timed out after 10 minutes.")
            return {"error": "SadTalker generation timed out (10 minutes)."}
        except Exception as e:
            logger.error(f"SadTalker generation failed: {e}")
            return {"error": str(e)}

    # ─── D-ID Cloud Engine (Paid) ─────────────────────────────────────────

    async def _did_generate(
        self, audio_url: str, presenter_image: str
    ) -> Dict[str, Any]:
        """Generate lip-sync video using D-ID Talks API."""
        create_url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Basic {self.did_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "source_url": presenter_image,
            "script": {
                "type": "audio",
                "audio_url": audio_url,
            },
            "config": {
                "result_format": "mp4",
            },
        }

        try:
            response = await http_client.post_json(create_url, payload, headers=headers)
            talk_data = response.json()
            talk_id = talk_data.get("id")

            if not talk_id:
                return {"error": "D-ID did not return a talk ID"}

            result_url = f"{create_url}/{talk_id}"
            max_wait = 300
            poll_interval = 5
            elapsed = 0

            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                poll_response = await http_client.poll_get(result_url, headers=headers)
                status_data = poll_response.json()

                status = status_data.get("status")
                if status == "done":
                    video_url = status_data.get("result_url")
                    if video_url:
                        local_path = await self._download_video(video_url)
                        return {
                            "path": local_path,
                            "url": f"/output/avatars/{os.path.basename(local_path)}",
                            "duration_seconds": status_data.get("duration", 0),
                            "engine": "did",
                        }
                elif status == "error":
                    return {"error": f"D-ID generation failed: {status_data.get('error', 'Unknown')}"}

            return {"error": "D-ID generation timed out (5 minutes)"}

        except httpx.HTTPStatusError as e:
            return {"error": f"D-ID API error: {e.response.status_code} - {e.response.text[:200]}"}
        except Exception as e:
            logger.error(f"D-ID generation failed: {e}")
            return {"error": str(e)}

    # ─── HeyGen Cloud Engine (Paid) ───────────────────────────────────────

    async def _heygen_generate(
        self, audio_url: str, presenter_image: str
    ) -> Dict[str, Any]:
        """Generate lip-sync video using HeyGen API."""
        create_url = "https://api.heygen.com/v2/video/generate"
        headers = {
            "X-Api-Key": self.heygen_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "photo",
                        "photo_url": presenter_image,
                    },
                    "voice": {
                        "type": "audio",
                        "audio_url": audio_url,
                    },
                }
            ],
            "dimension": {"width": 1920, "height": 1080},
        }

        try:
            response = await http_client.post_json(create_url, payload, headers=headers)
            data = response.json()
            video_id = data.get("data", {}).get("video_id")

            if not video_id:
                return {"error": "HeyGen did not return a video ID"}

            status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
            max_wait = 300
            poll_interval = 10
            elapsed = 0

            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                poll_response = await http_client.poll_get(status_url, headers=headers)
                status_data = poll_response.json()

                status = status_data.get("data", {}).get("status")
                if status == "completed":
                    video_url = status_data.get("data", {}).get("video_url")
                    if video_url:
                        local_path = await self._download_video(video_url)
                        return {
                            "path": local_path,
                            "url": f"/output/avatars/{os.path.basename(local_path)}",
                            "duration_seconds": status_data.get("data", {}).get("duration", 0),
                            "engine": "heygen",
                        }
                elif status == "failed":
                    return {"error": "HeyGen video generation failed"}

            return {"error": "HeyGen generation timed out (5 minutes)"}

        except Exception as e:
            logger.error(f"HeyGen generation failed: {e}")
            return {"error": str(e)}

    # ─── Utility ──────────────────────────────────────────────────────────

    async def _download_video(self, url: str) -> str:
        """Download a video from URL to local storage."""
        filename = f"avatar_{uuid.uuid4().hex[:12]}.mp4"
        local_path = os.path.join(self.output_dir, filename)
        await http_client.download_file(url, local_path)
        logger.info(f"Avatar video downloaded: {local_path}")
        return local_path


avatar_service = AvatarService()
