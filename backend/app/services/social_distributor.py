"""
Social Distribution Service
Central router for posting content to multiple platforms.
"""
import logging
from typing import List, Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

class SocialDistributor:
    """Orchestrates content distribution across multiple social platforms."""

    def __init__(self):
        self.platforms = {}
        self._initialize_platforms()

    def _initialize_platforms(self):
        """Lazy-load platform services to avoid circular imports or unnecessary dependency loading."""
        try:
            from app.services.platforms.telegram_service import telegram_service
            self.platforms["telegram"] = telegram_service
        except ImportError as e:
            logger.warning(f"Telegram service not available: {e}")

        try:
            from app.services.platforms.youtube_service import youtube_service
            self.platforms["youtube"] = youtube_service
        except ImportError as e:
            logger.warning(f"YouTube service not available: {e}")

        try:
            from app.services.platforms.twitter_service import twitter_service
            self.platforms["twitter"] = twitter_service
        except ImportError as e:
            logger.warning(f"Twitter service not available: {e}")

        try:
            from app.services.platforms.discord_service import discord_service
            self.platforms["discord"] = discord_service
        except ImportError as e:
            logger.warning(f"Discord service not available: {e}")

    async def distribute(
        self, 
        content_type: str, 
        platforms: List[str], 
        params: Dict[str, Any],
        profile_configs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Distribute content to selected platforms.
        
        Args:
            content_type: "video", "report", or "summary"
            platforms: List of platform keys (e.g., ["telegram", "youtube"])
            params: Dictionary containing media paths, titles, descriptions, etc.
            profile_configs: Optional platform-specific credentials from a Profile
        """
        results = {}
        
        for platform_key in platforms:
            if platform_key not in self.platforms:
                results[platform_key] = {"status": "error", "message": f"Platform '{platform_key}' not supported or configured"}
                continue
            
            platform_service = self.platforms[platform_key]
            # Get specific config for this platform from the profile
            platform_config = (profile_configs or {}).get(platform_key, {})
            
            try:
                logger.info(f"Distributing {content_type} to {platform_key}...")
                
                if content_type == "video":
                    res = await platform_service.post_video(
                        video_path=params.get("video_path"),
                        title=params.get("title", ""),
                        description=params.get("description", ""),
                        thumbnail_path=params.get("thumbnail_path"),
                        config=platform_config
                    )
                elif content_type == "report":
                    res = await platform_service.post_text(
                        text=params.get("text", ""),
                        title=params.get("title", ""),
                        config=platform_config
                    )
                else:
                    results[platform_key] = {"status": "error", "message": f"Content type '{content_type}' not supported"}
                    continue
                
                results[platform_key] = res
            except Exception as e:
                logger.error(f"Failed to post to {platform_key}: {e}")
                results[platform_key] = {"status": "error", "message": str(e)}
        
        return results

    def get_supported_platforms(self) -> List[str]:
        """Return list of platforms currently implemented."""
        return list(self.platforms.keys())

social_distributor = SocialDistributor()
