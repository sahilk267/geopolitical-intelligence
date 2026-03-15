"""
Seed Script for Live Verification Campaign (Local AI + RAG + Distribution)
"""
import asyncio
import logging
import os
from uuid import UUID

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.campaign import Campaign

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_live_test():
    async with AsyncSessionLocal() as db:
        # 1. Find Admin User
        result = await db.execute(select(User).where(User.primary_role == UserRole.ADMIN).limit(1))
        admin = result.scalar_one_or_none()
        
        if not admin:
            result = await db.execute(select(User).limit(1))
            admin = result.scalar_one_or_none()
            
        if not admin:
            logger.error("No user found in database. Run seed_automation.py first.")
            return

        # 2. Create "Geopolitical Sentinel" Profile (Optimized for Local AI)
        profile_name = "Geopolitical Sentinel (Live Test)"
        result = await db.execute(select(Profile).where(Profile.name == profile_name))
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = Profile(
                name=profile_name,
                description="Fast-response persona utilizing local Ollama, SD.Next, and SadTalker for autonomous intelligence delivery.",
                voice_engine="edge-tts",
                voice_id="en-US-SteffanNeural",
                video_style={
                    "backgroundColor": "#1e293b",
                    "textColor": "#ffffff",
                    "theme": "modern-compact",
                    "avatar": {
                        "engine": "local",
                        "presenter_image": "./assets/presenter.png"
                    }
                },
                platform_configs={
                    "discord": {"channel_name": "intel-reports"},
                    "telegram": {"channel_id": "test_geopol_intel"}
                },
                created_by=admin.id
            )
            db.add(profile)
            await db.flush()
            logger.info(f"Created profile: {profile.name}")
        else:
            logger.info(f"Profile {profile_name} already exists.")

        # 3. Create "Global Conflict Monitoring" Campaign
        campaign_name = "Global Conflict Monitoring"
        result = await db.execute(select(Campaign).where(Campaign.name == campaign_name))
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            campaign = Campaign(
                name=campaign_name,
                description="Live verification mission to test local inference, talking head generation, and Discord/Telegram distribution.",
                profile_id=profile.id,
                categories=["Military", "Security", "Conflict"],
                regions=["Global"],
                schedule_type="hourly",
                is_active=True,
                created_by=admin.id
            )
            db.add(campaign)
            logger.info(f"Created campaign: {campaign.name}")
        else:
            logger.info(f"Campaign {campaign_name} already exists.")

        await db.commit()
        logger.info("Live Verification Seeding completed. You can now trigger this in the UI or via Analytics.")

if __name__ == "__main__":
    asyncio.run(seed_live_test())
