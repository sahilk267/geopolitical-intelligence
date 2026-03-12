"""
Platform Settings API Endpoints
Manages runtime configuration from the SuperAdmin panel.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.setting import PlatformSetting
from app.models.user import UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


# Default settings to seed if table is empty
DEFAULT_SETTINGS = {
    "safe_mode_enabled": {"value": "false", "category": "security", "description": "Enable Safe Mode to prevent database writes"},
    "risk_threshold": {"value": "40", "category": "security", "description": "Risk threshold for content flagging (0-100)"},
    "auto_publish_enabled": {"value": "false", "category": "general", "description": "Auto-publish approved content"},
    "tts_engine": {"value": "edge_tts", "category": "tts", "description": "TTS engine: elevenlabs, edge_tts, piper, or gtts"},
    "tts_voice_id": {"value": "en-US-GuyNeural", "category": "tts", "description": "Default TTS voice ID"},
    "edge_tts_voice": {"value": "en-US-GuyNeural", "category": "tts", "description": "Default voice for Edge-TTS"},
    "piper_tts_model": {"value": "en_US-lessac-medium", "category": "tts", "description": "Default model for Piper TTS"},
    "avatar_engine": {"value": "did", "category": "video", "description": "Avatar engine: did or heygen"},
    "default_video_resolution": {"value": "1920x1080", "category": "video", "description": "Default video resolution"},
    "short_clip_duration": {"value": "45", "category": "video", "description": "Default short clip duration in seconds"},
    "auto_fetch_interval": {"value": "30", "category": "general", "description": "Auto-fetch interval in minutes"},
    "ai_provider": {"value": "gemini", "category": "ai", "description": "AI provider: gemini or ollama"},
    "gemini_model": {"value": "gemini-1.5-pro", "category": "ai", "description": "Gemini model to use"},
    "ollama_base_url": {"value": "http://host.docker.internal:11434", "category": "ai", "description": "Ollama API Base URL"},
    "ollama_model": {"value": "llama3.2", "category": "ai", "description": "Ollama model name"},
    "telegram_bot_token": {"value": "", "category": "distribution", "description": "Telegram Bot Token from @BotFather"},
    "telegram_chat_id": {"value": "", "category": "distribution", "description": "Telegram Channel/Group Chat ID"},
    "youtube_client_id": {"value": "", "category": "distribution", "description": "YouTube API Client ID"},
    "youtube_client_secret": {"value": "", "category": "distribution", "description": "YouTube API Client Secret"},
}


@router.get("/")
async def get_all_settings(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get all platform settings, optionally filtered by category."""
    query = select(PlatformSetting)
    if category:
        query = query.where(PlatformSetting.category == category)

    result = await db.execute(query)
    settings = result.scalars().all()

    # If no settings exist, seed defaults
    if not settings and not category:
        for key, data in DEFAULT_SETTINGS.items():
            setting = PlatformSetting(
                key=key,
                value=data["value"],
                category=data["category"],
                description=data["description"],
            )
            db.add(setting)
        await db.commit()

        result = await db.execute(select(PlatformSetting))
        settings = result.scalars().all()

    return [s.to_dict() for s in settings]


@router.put("/")
async def update_settings(
    updates: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(UserRole.EDITOR_IN_CHIEF)),
):
    """Update one or more platform settings (admin only)."""
    updated = []
    from app.core.config import settings as app_settings

    for key, value in updates.items():
        result = await db.execute(
            select(PlatformSetting).where(PlatformSetting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            setting.updated_by = current_user.id
            updated.append(key)
        else:
            # Create new setting
            new_setting = PlatformSetting(
                key=key,
                value=value,
                category="general",
                updated_by=current_user.id,
            )
            db.add(new_setting)
            updated.append(key)

        # Dynamically update in-memory config for AI variables
        if key == "ai_provider":
            app_settings.AI_PROVIDER = value
        elif key == "ollama_base_url":
            app_settings.OLLAMA_BASE_URL = value
        elif key == "ollama_model":
            app_settings.OLLAMA_MODEL = value
        elif key == "telegram_bot_token":
            app_settings.TELEGRAM_BOT_TOKEN = value
            from app.services.platforms.telegram_service import telegram_service
            telegram_service.bot_token = value
            telegram_service.api_url = f"https://api.telegram.org/bot{value}" if value else None
        elif key == "telegram_chat_id":
            app_settings.TELEGRAM_CHAT_ID = value
            from app.services.platforms.telegram_service import telegram_service
            telegram_service.chat_id = value
        elif key == "youtube_client_id":
            app_settings.YOUTUBE_CLIENT_ID = value
        elif key == "youtube_client_secret":
            app_settings.YOUTUBE_CLIENT_SECRET = value
        elif key == "tts_engine":
            app_settings.TTS_ENGINE = value
            from app.services.tts_service import tts_service
            tts_service.reload_settings()
        elif key == "edge_tts_voice":
            app_settings.EDGE_TTS_VOICE = value
            from app.services.tts_service import tts_service
            tts_service.reload_settings()
        elif key == "piper_tts_model":
            app_settings.PIPER_TTS_MODEL = value
            from app.services.tts_service import tts_service
            tts_service.reload_settings()

    await db.commit()
    return {"updated": updated, "count": len(updated)}


@router.post("/api-keys")
async def update_api_keys(
    gemini_key: Optional[str] = None,
    elevenlabs_key: Optional[str] = None,
    did_key: Optional[str] = None,
    heygen_key: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(UserRole.EDITOR_IN_CHIEF)),
):
    """Securely update API keys (admin only). Keys are stored encrypted."""
    keys_updated = []

    key_map = {
        "gemini_api_key": gemini_key,
        "elevenlabs_api_key": elevenlabs_key,
        "did_api_key": did_key,
        "heygen_api_key": heygen_key,
    }

    from app.core.config import settings as app_settings
    from app.core.encryption import encrypt_value, mask_key
    
    for key_name, key_value in key_map.items():
        if key_value is not None:
            # First fetch from database
            result = await db.execute(
                select(PlatformSetting).where(PlatformSetting.key == key_name)
            )
            setting = result.scalar_one_or_none()

            # Mask the key for display
            masked = mask_key(key_value)

            # Encrypt the key before storing in database
            encrypted_value = encrypt_value(key_value)

            if setting:
                setting.value = encrypted_value
                setting.updated_at = datetime.utcnow()
                setting.updated_by = current_user.id
            else:
                db.add(PlatformSetting(
                    key=key_name,
                    value=encrypted_value,
                    category="security",
                    description=f"API key for {key_name.replace('_', ' ').title()}",
                    updated_by=current_user.id,
                ))

            # Dynamically update the in-memory settings across the app
            if key_name == "gemini_api_key":
                app_settings.GEMINI_API_KEY = key_value
                import google.generativeai as genai
                genai.configure(api_key=key_value)
                try:
                    from app.services.ai_service import ai_service
                    ai_service.model = genai.GenerativeModel(app_settings.LLM_MODEL)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to reinitialize Gemini model after key update: {e}")
            elif key_name == "elevenlabs_api_key":
                app_settings.ELEVENLABS_API_KEY = key_value
            elif key_name == "did_api_key":
                app_settings.DID_API_KEY = key_value
            elif key_name == "heygen_api_key":
                app_settings.HEYGEN_API_KEY = key_value

            keys_updated.append({"key": key_name, "masked": masked})

    await db.commit()
    return {"updated": keys_updated}


@router.get("/api-keys/test")
async def test_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(UserRole.EDITOR_IN_CHIEF)),
):
    """Test validity of configured API keys."""
    from app.core.config import settings
    import httpx

    results = {}

    from app.core.encryption import decrypt_value

    # Read latest from DB, decrypt if needed
    result = await db.execute(select(PlatformSetting).where(PlatformSetting.category == "security"))
    settings_db = {s.key: decrypt_value(s.value) for s in result.scalars().all()}
    
    gemini_key = settings_db.get("gemini_api_key") or settings.GEMINI_API_KEY
    elevenlabs_key = settings_db.get("elevenlabs_api_key") or settings.ELEVENLABS_API_KEY
    did_key = settings_db.get("did_api_key") or settings.DID_API_KEY
    heygen_key = settings_db.get("heygen_api_key") or settings.HEYGEN_API_KEY

    # Test Gemini
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            model.generate_content("test")
            results["gemini"] = {"status": "valid", "key_set": True}
        except Exception as e:
            results["gemini"] = {"status": "invalid", "error": str(e)[:100]}
    else:
        results["gemini"] = {"status": "not_configured", "key_set": False}

    # Test ElevenLabs
    if elevenlabs_key:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers={"xi-api-key": elevenlabs_key},
                )
                results["elevenlabs"] = {"status": "valid" if resp.status_code == 200 else "invalid", "key_set": True}
        except Exception as e:
            results["elevenlabs"] = {"status": "error", "error": str(e)[:100]}
    else:
        results["elevenlabs"] = {"status": "not_configured", "key_set": False}

    # Test D-ID
    if did_key:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.d-id.com/credits",
                    headers={"Authorization": f"Basic {did_key}"},
                )
                results["did"] = {"status": "valid" if resp.status_code == 200 else "invalid", "key_set": True}
        except Exception as e:
            results["did"] = {"status": "error", "error": str(e)[:100]}
    else:
        results["did"] = {"status": "not_configured", "key_set": False}

    # Test HeyGen
    if heygen_key:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.heygen.com/v2/templates",
                    headers={"X-Api-Key": heygen_key},
                )
                results["heygen"] = {"status": "valid" if resp.status_code == 200 else "invalid", "key_set": True}
        except Exception as e:
            results["heygen"] = {"status": "error", "error": str(e)[:100]}
    else:
        results["heygen"] = {"status": "not_configured", "key_set": False}

    # Test Ollama
    ollama_base_url = settings_db.get("ollama_base_url") or settings.OLLAMA_BASE_URL
    if ollama_base_url:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{ollama_base_url.rstrip('/')}/api/tags")
                results["ollama"] = {"status": "valid" if resp.status_code == 200 else "invalid", "key_set": True}
        except Exception as e:
            results["ollama"] = {"status": "error", "error": str(e)[:100]}
    else:
        results["ollama"] = {"status": "not_configured", "key_set": False}

    return results
