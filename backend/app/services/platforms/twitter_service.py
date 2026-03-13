"""
X/Twitter Distribution Service
Posts text and video content to X/Twitter via API v2 (OAuth 1.0a).
"""
import os
import logging
from typing import Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TwitterService:
    """Service for posting content to X/Twitter."""

    def __init__(self):
        self.api_key = getattr(settings, "TWITTER_API_KEY", None)
        self.api_secret = getattr(settings, "TWITTER_API_SECRET", None)
        self.access_token = getattr(settings, "TWITTER_ACCESS_TOKEN", None)
        self.access_secret = getattr(settings, "TWITTER_ACCESS_SECRET", None)

    def _get_client(self, config: Optional[Dict[str, Any]] = None):
        """Get authenticated tweepy client. Supports profile-specific overrides."""
        try:
            import tweepy
        except ImportError:
            raise ImportError("tweepy not installed. Run: pip install tweepy")

        api_key = (config or {}).get("api_key") or self.api_key
        api_secret = (config or {}).get("api_secret") or self.api_secret
        access_token = (config or {}).get("access_token") or self.access_token
        access_secret = (config or {}).get("access_secret") or self.access_secret

        if not all([api_key, api_secret, access_token, access_secret]):
            return None, None

        # V2 client for text tweets
        client_v2 = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

        # V1.1 API for media uploads (required for videos/images)
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        api_v1 = tweepy.API(auth)

        return client_v2, api_v1

    async def post_text(
        self, text: str, title: str = "", config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Post a text tweet."""
        client_v2, _ = self._get_client(config)

        if not client_v2:
            return {"status": "error", "message": "Twitter not configured (API keys missing)"}

        tweet_text = f"📊 {title}\n\n{text}" if title else text

        # Twitter has a 280 char limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        try:
            response = client_v2.create_tweet(text=tweet_text)
            tweet_id = response.data.get("id") if response.data else None
            logger.info(f"Twitter: posted tweet {tweet_id}")
            return {
                "status": "success",
                "platform": "twitter",
                "tweet_id": tweet_id,
                "url": f"https://x.com/i/status/{tweet_id}" if tweet_id else None,
            }
        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return {"status": "error", "message": str(e)}

    async def post_video(
        self,
        video_path: str,
        title: str = "",
        description: str = "",
        thumbnail_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Post a video tweet with media upload."""
        client_v2, api_v1 = self._get_client(config)

        if not client_v2 or not api_v1:
            return {"status": "error", "message": "Twitter not configured (API keys missing)"}

        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        try:
            # Upload media using v1.1 API (chunked for large files)
            media = api_v1.media_upload(
                filename=video_path,
                media_category="tweet_video",
            )
            logger.info(f"Twitter: uploaded media {media.media_id}")

            # Create tweet with media using v2 API
            tweet_text = f"🎬 {title}" if title else "🌐 Geopolitical Intelligence Update"
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."

            response = client_v2.create_tweet(
                text=tweet_text,
                media_ids=[media.media_id],
            )
            tweet_id = response.data.get("id") if response.data else None
            logger.info(f"Twitter: posted video tweet {tweet_id}")
            return {
                "status": "success",
                "platform": "twitter",
                "tweet_id": tweet_id,
                "url": f"https://x.com/i/status/{tweet_id}" if tweet_id else None,
            }
        except Exception as e:
            logger.error(f"Twitter video post failed: {e}")
            return {"status": "error", "message": str(e)}


twitter_service = TwitterService()
