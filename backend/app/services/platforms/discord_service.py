"""
Discord Distribution Service
Posts content to Discord channels via webhooks (no bot token required).
"""
import os
import logging
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class DiscordService:
    """Service for posting content to Discord via webhooks."""

    def __init__(self):
        self.webhook_url = getattr(settings, "DISCORD_WEBHOOK_URL", None)

    async def post_text(
        self, text: str, title: str = "", config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post a rich embed message to Discord."""
        webhook_url = (config or {}).get("webhook_url") or self.webhook_url

        if not webhook_url:
            return {"status": "error", "message": "Discord not configured (webhook URL missing)"}

        # Build a rich embed
        embed = {
            "title": title or "📊 Geopolitical Intelligence Update",
            "description": text[:4096],  # Discord embed limit
            "color": 0x1E90FF,  # DodgerBlue
            "footer": {"text": "Geopolitical Intelligence Platform"},
        }

        payload = {
            "embeds": [embed],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(webhook_url, json=payload)
                resp.raise_for_status()

            logger.info(f"Discord: posted embed '{title}'")
            return {
                "status": "success",
                "platform": "discord",
                "message": "Embed posted successfully",
            }
        except Exception as e:
            logger.error(f"Discord post failed: {e}")
            return {"status": "error", "message": str(e)}

    async def post_video(
        self,
        video_path: str,
        title: str = "",
        description: str = "",
        thumbnail_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Post a video file to Discord via webhook with multipart upload."""
        webhook_url = (config or {}).get("webhook_url") or self.webhook_url

        if not webhook_url:
            return {"status": "error", "message": "Discord not configured (webhook URL missing)"}

        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        file_size = os.path.getsize(video_path)
        max_size = 25 * 1024 * 1024  # 25MB Discord limit (free tier)

        if file_size > max_size:
            # Fallback: post text embed with file size note
            return await self._post_oversized_fallback(webhook_url, title, description, file_size)

        try:
            embed_payload = {
                "embeds": [{
                    "title": f"🎬 {title}" if title else "🎬 Intelligence Briefing",
                    "description": (description or "")[:1024],
                    "color": 0xFF4500,  # OrangeRed
                    "footer": {"text": "Geopolitical Intelligence Platform"},
                }]
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                import json as json_lib
                with open(video_path, "rb") as f:
                    files = {
                        "file": (os.path.basename(video_path), f, "video/mp4"),
                    }
                    data = {
                        "payload_json": json_lib.dumps(embed_payload),
                    }
                    resp = await client.post(webhook_url, data=data, files=files)
                    resp.raise_for_status()

            logger.info(f"Discord: posted video '{title}' ({file_size // 1024}KB)")
            return {
                "status": "success",
                "platform": "discord",
                "message": f"Video uploaded ({file_size // 1024}KB)",
            }
        except Exception as e:
            logger.error(f"Discord video post failed: {e}")
            return {"status": "error", "message": str(e)}

    async def _post_oversized_fallback(
        self, webhook_url: str, title: str, description: str, file_size: int
    ) -> Dict[str, Any]:
        """Post a text-only message when the video exceeds Discord's upload limit."""
        embed = {
            "title": f"🎬 {title}" if title else "🎬 Intelligence Briefing",
            "description": f"{(description or '')[:1024]}\n\n⚠️ Video too large for Discord ({file_size // (1024*1024)}MB). Available on the dashboard.",
            "color": 0xFFA500,
            "footer": {"text": "Geopolitical Intelligence Platform"},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(webhook_url, json={"embeds": [embed]})
                resp.raise_for_status()
            return {"status": "success", "platform": "discord", "message": "Text fallback (video too large)"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


discord_service = DiscordService()
