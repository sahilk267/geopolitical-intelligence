import asyncio
from app.db.base import AsyncSessionLocal
from app.models.campaign import Campaign
from sqlalchemy import select

async def update_campaign():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Campaign).where(Campaign.name == 'Economic Intelligence Mission'))
        campaign = result.scalar_one_or_none()
        if campaign:
            campaign.categories = ["Regional News"]
            campaign.last_run_at = None # Reset to trigger immediately
            await db.commit()
            print("Campaign categories updated to ['Regional News']")
        else:
            print("Campaign not found")

if __name__ == "__main__":
    asyncio.run(update_campaign())
