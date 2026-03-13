"""
YouTube Distribution Service
Uploads videos to YouTube using Data API v3.
Token persistence via database-backed storage in PlatformSetting.
"""
import os
import json
import logging
from typing import Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Guard imports — these may not be installed in all environments
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False
    logger.warning("Google API libraries not installed. YouTube integration unavailable.")


class YouTubeService:
    """Service for interacting with YouTube Data API v3."""

    def __init__(self):
        self.client_id = settings.YOUTUBE_CLIENT_ID
        self.client_secret = settings.YOUTUBE_CLIENT_SECRET
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        # Legacy filesystem path (fallback)
        self.token_path = os.path.join(os.path.dirname(settings.VIDEO_OUTPUT_DIR), "youtube_token.json")

    def _get_credentials(self, config: Optional[Dict[str, Any]] = None) -> Optional["Credentials"]:
        """
        Load OAuth credentials. Priority:
        1. Config-provided token (from Profile platform_configs)
        2. Database-stored token (PlatformSetting with key='youtube_oauth_token')
        3. Legacy filesystem token file
        """
        if not HAS_GOOGLE_LIBS:
            return None

        # 1. Try config-provided token first
        token_json = (config or {}).get("oauth_token")
        if token_json:
            try:
                creds = Credentials.from_authorized_user_info(json.loads(token_json), self.scopes)
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                return creds
            except Exception as e:
                logger.warning(f"Failed to load YouTube token from provided config: {e}")

        # Try database first (synchronous read for credential loading)
        try:
            token_json = self._load_token_from_db()
            if token_json:
                creds = Credentials.from_authorized_user_info(json.loads(token_json), self.scopes)
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self._save_token_to_db(creds.to_json())
                return creds
        except Exception as e:
            logger.warning(f"Failed to load YouTube token from database: {e}")

        # Fallback to filesystem
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_path, "w") as token:
                        token.write(creds.to_json())
                    # Migrate to database for future use
                    self._save_token_to_db(creds.to_json())
                return creds
            except Exception as e:
                logger.warning(f"Failed to load YouTube token from filesystem: {e}")

        return None

    def _load_token_from_db(self) -> Optional[str]:
        """Load token JSON string from database synchronously."""
        try:
            from app.core.encryption import decrypt_value
            # Use a sync database query for credential loading
            from sqlalchemy import create_engine, text
            from app.core.config import settings as app_settings

            db_url = app_settings.SQLALCHEMY_DATABASE_URI
            if not db_url:
                return None

            # Convert async URL to sync
            sync_url = db_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
            engine = create_engine(sync_url)
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT value FROM platform_settings WHERE key = :key"),
                    {"key": "youtube_oauth_token"}
                )
                row = result.fetchone()
                if row:
                    return decrypt_value(row[0])
        except Exception as e:
            logger.debug(f"DB token load skipped: {e}")
        return None

    def _save_token_to_db(self, token_json: str):
        """Save token JSON string to database."""
        try:
            from app.core.encryption import encrypt_value
            from sqlalchemy import create_engine, text
            from app.core.config import settings as app_settings

            db_url = app_settings.SQLALCHEMY_DATABASE_URI
            if not db_url:
                return

            sync_url = db_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
            encrypted = encrypt_value(token_json)
            engine = create_engine(sync_url)
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO platform_settings (key, value, category, description)
                        VALUES (:key, :value, :category, :description)
                        ON CONFLICT (key) DO UPDATE SET value = :value
                    """),
                    {
                        "key": "youtube_oauth_token",
                        "value": encrypted,
                        "category": "security",
                        "description": "YouTube OAuth2 refresh token (encrypted)",
                    }
                )
                conn.commit()
            logger.info("YouTube OAuth token saved to database.")
        except Exception as e:
            logger.warning(f"Failed to save YouTube token to database: {e}")

    async def post_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        thumbnail_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload a video to YouTube."""
        if not HAS_GOOGLE_LIBS:
            return {"status": "error", "message": "Google API libraries not installed."}

        creds = self._get_credentials(config=config)
        if not creds:
            return {"status": "error", "message": "YouTube not authenticated. Please connect your account in Settings."}

        try:
            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags or ["geopolitics", "intelligence", "news"],
                    "categoryId": "25"  # News & Politics
                },
                "status": {
                    "privacyStatus": "unlisted",  # Default to unlisted for review
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"YouTube Upload Progress: {int(status.progress() * 100)}%")

            video_id = response.get("id")

            # If thumbnail exists, upload it
            if video_id and thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(thumbnail_path)
                    ).execute()
                except Exception as e:
                    logger.warning(f"Failed to upload YouTube thumbnail: {e}")

            return {
                "status": "success",
                "platform": "youtube",
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }

        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return {"status": "error", "message": str(e)}

    async def test_connection(self) -> Dict[str, Any]:
        """Check if YouTube credentials are valid."""
        if not HAS_GOOGLE_LIBS:
            return {"status": "error", "message": "Google API libraries not installed."}

        creds = self._get_credentials()
        if not creds:
            return {"status": "error", "message": "No credentials found"}

        try:
            youtube = build("youtube", "v3", credentials=creds)
            channels = youtube.channels().list(part="snippet", mine=True).execute()

            if "items" in channels:
                channel = channels["items"][0]["snippet"]
                return {
                    "status": "success",
                    "channel_name": channel["title"],
                    "thumbnail": channel["thumbnails"]["default"]["url"]
                }
            return {"status": "error", "message": "No YouTube channel found for this account"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

youtube_service = YouTubeService()
