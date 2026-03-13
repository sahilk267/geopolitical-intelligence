"""
Seed Script for Initial Profile and Campaign
"""
import asyncio
import logging
from uuid import UUID

from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.campaign import Campaign

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_automation():
    async with AsyncSessionLocal() as db:
        # 1. Find Admin User
        result = await db.execute(select(User).where(User.primary_role == UserRole.ADMIN).limit(1))
        admin = result.scalar_one_or_none()
        
        if not admin:
            # Try any user
            result = await db.execute(select(User).limit(1))
            admin = result.scalar_one_or_none()
            
        if not admin:
            logger.error("No user found in database to own the profile. Please run create-initial-data first.")
            return

        logger.info(f"Seeding for user: {admin.full_name} ({admin.email})")

        # 2. Create Profile: Global Strategic Analyst
        profile_name = "Global Strategic Analyst"
        result = await db.execute(select(Profile).where(Profile.name == profile_name))
        existing_profile = result.scalar_one_or_none()
        
        if not existing_profile:
            profile = Profile(
                name=profile_name,
                description="Professional, analytical persona for high-level geopolitical and economic insights.",
                voice_engine="edge-tts",
                voice_id="en-US-GuyNeural",
                video_style={
                    "backgroundColor": "#0f172a",
                    "textColor": "#f8fafc",
                    "font": "Inter",
                    "theme": "cinematic"
                },
                platform_configs={
                    "telegram": {"channel_id": "@geopol_intel_test"},
                    "youtube": {"category": "News"}
                },
                created_by=admin.id
            )
            db.add(profile)
            await db.flush()
            logger.info(f"Created profile: {profile.name}")
        else:
            profile = existing_profile
            logger.info(f"Profile {profile_name} already exists.")

        # 3. Create Campaign: Economic Intelligence Mission
        campaign_name = "Economic Intelligence Mission"
        result = await db.execute(select(Campaign).where(Campaign.name == campaign_name))
        existing_campaign = result.scalar_one_or_none()
        
        if not existing_campaign:
            campaign = Campaign(
                name=campaign_name,
                description="Autonomous daily briefing on global trade, finance, and economic risk.",
                profile_id=profile.id,
                categories=["Economics", "Finance", "Trade"],
                regions=["Global"],
                schedule_type="daily",
                is_active=True,
                created_by=admin.id
            )
            db.add(campaign)
            logger.info(f"Created campaign: {campaign.name}")
        else:
            logger.info(f"Campaign {campaign_name} already exists.")

        await db.commit()
        logger.info("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_automation())
