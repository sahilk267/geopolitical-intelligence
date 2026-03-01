import asyncio
import logging
from app.db.base import engine, Base
from app.db.init_db import init_db, create_initial_data
from app.db.base import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_database():
    logger.info("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.info("Initializing fresh database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        await create_initial_data(session)
    
    logger.info("Database reset and seeding complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
