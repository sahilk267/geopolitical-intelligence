
import asyncio
from app.db.base import engine, Base
from app.models.user import User
from app.models.article import RawArticle, NormalizedArticle
from app.models.source import Source
from app.models.script import Script
from app.models.profile import Profile
from app.models.entity import Entity, ArticleEntity
from app.models.claim import Claim
from app.models.risk import RiskScore

async def init_db():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
