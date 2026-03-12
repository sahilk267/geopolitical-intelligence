"""
Telegram Distribution Service
Posts videos and reports to Telegram channels/groups via Bot API.
"""
import os
import logging
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.http_client import http_client

logger = logging.getLogger(__name__)

class TelegramService:
    """Service for interacting with Telegram Bot API."""

    def __init__(self):
        self.bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        self.chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    async def post_text(self, text: str, title: str = "") -> Dict[str, Any]:
        """Post a text report to Telegram."""
        if not self.api_url or not self.chat_id:
            return {"status": "error", "message": "Telegram not configured (token or chat_id missing)"}

        message = f"<b>{title}</b>\n\n{text}" if title else text
        
        # Telegram has a 4096 char limit for text
        if len(message) > 4000:
            message = message[:4000] + "..."

        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = await http_client.post_json(url, payload)
            data = response.json()
                
            if data.get("ok"):
                return {"status": "success", "platform": "telegram", "message_id": data["result"]["message_id"]}
            else:
                return {"status": "error", "message": data.get("description", "Unknown Telegram error")}
        except Exception as e:
            logger.error(f"Telegram post_text failed: {e}")
            return {"status": "error", "message": str(e)}

    async def post_video(
        self, 
        video_path: str, 
        title: str = "", 
        description: str = "",
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post a video file to Telegram."""
        if not self.api_url or not self.chat_id:
            return {"status": "error", "message": "Telegram not configured"}

        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        url = f"{self.api_url}/sendVideo"
        caption = f"<b>{title}</b>\n\n{description}" if title else description
        
        # Telegram has a 1024 char limit for captions
        if len(caption) > 1000:
            caption = caption[:1000] + "..."

        try:
            files = {
                "video": (os.path.basename(video_path), open(video_path, "rb"), "video/mp4")
            }
                
            if thumbnail_path and os.path.exists(thumbnail_path):
                files["thumb"] = (os.path.basename(thumbnail_path), open(thumbnail_path, "rb"), "image/jpeg")
                
            data = {
                "chat_id": self.chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
                
            response = await http_client.post_multipart(url, data=data, files=files, timeout=120.0)
            # Close files
            for f in files.values():
                if hasattr(f[1], "close"):
                    f[1].close()
                        
            res_data = response.json()
                
            if res_data.get("ok"):
                return {"status": "success", "platform": "telegram", "message_id": res_data["result"]["message_id"]}
            else:
                return {"status": "error", "message": res_data.get("description", "Unknown Telegram error")}
        except Exception as e:
            logger.error(f"Telegram post_video failed: {e}")
            return {"status": "error", "message": str(e)}

telegram_service = TelegramService()
