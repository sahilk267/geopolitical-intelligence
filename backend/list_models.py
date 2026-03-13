import google.generativeai as genai
import os
from app.core.config import settings
from app.db.base import AsyncSessionLocal
from app.models.setting import PlatformSetting
import asyncio
from sqlalchemy import select

async def list_models():
    # Use database key if available
    from app.db.base import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PlatformSetting).where(PlatformSetting.key == "gemini_api_key"))
        setting = result.scalar_one_or_none()
        api_key = setting.value if setting else settings.GEMINI_API_KEY
        
    print(f"Using API Key: {api_key[:10]}...")
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
