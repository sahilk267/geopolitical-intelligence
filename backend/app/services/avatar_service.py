"""
Avatar / Lip-Sync Service
Generates lip-synced presenter videos using D-ID or HeyGen API.
"""
import os
import uuid
import asyncio
import logging
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.http_client import http_client

logger = logging.getLogger(__name__)


class AvatarService:
    """Generates lip-synced presenter videos using external APIs."""

    def __init__(self):
        self.engine = getattr(settings, "AVATAR_ENGINE", "did")
        self.did_api_key = getattr(settings, "DID_API_KEY", None)
        self.heygen_api_key = getattr(settings, "HEYGEN_API_KEY", None)
        self.default_presenter = getattr(
            settings, "DEFAULT_PRESENTER_IMAGE", "./assets/presenter.png"
        )
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
        
        # D-ID requires a public URL for the source image.
        # If the image is a local path (starts with . or /), D-ID will fail.
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
            logger.warning("No avatar API key configured. Returning placeholder.")
            return {
                "error": "No avatar/lip-sync API configured. Set DID_API_KEY or HEYGEN_API_KEY.",
                "fallback": True,
            }

    async def _did_generate(
        self, audio_url: str, presenter_image: str
    ) -> Dict[str, Any]:
        """Generate lip-sync video using D-ID Talks API."""
        create_url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Basic {self.did_api_key}",
            "Content-Type": "application/json",
        }

        # Step 1: Create talk
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

            # Step 2: Poll for completion
            result_url = f"{create_url}/{talk_id}"
            max_wait = 300  # 5 minutes
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
                        # Download the video
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

    async def _heygen_generate(
        self, audio_url: str, presenter_image: str
    ) -> Dict[str, Any]:
        """Generate lip-sync video using HeyGen API."""
        # HeyGen v2 API
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

            # Poll for completion
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

    async def _download_video(self, url: str) -> str:
        """Download a video from URL to local storage."""
        filename = f"avatar_{uuid.uuid4().hex[:12]}.mp4"
        local_path = os.path.join(self.output_dir, filename)
        await http_client.download_file(url, local_path)
        logger.info(f"Avatar video downloaded: {local_path}")
        return local_path


avatar_service = AvatarService()
