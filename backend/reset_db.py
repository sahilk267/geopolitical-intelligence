import asyncio
import logging
from sqlalchemy import text
from app.db.base import engine
from app.db.init_db import init_db, create_initial_data
from app.db.base import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_database():
    logger.info("Dropping and recreating public schema...")
    async with engine.begin() as conn:
        # Postgres specific cascade drop of the entire schema
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    
    logger.info("Initializing fresh database tables...")
    await init_db()
    
    logger.info("Seeding initial data...")
    async with AsyncSessionLocal() as session:
        await create_initial_data(session)
    
    logger.info("Database reset and seeding successfully complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
