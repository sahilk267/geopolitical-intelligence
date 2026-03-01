import asyncio
import logging
from sqlalchemy import text
from app.db.base import engine, Base
from app.db.init_db import init_db, create_initial_data
from app.db.base import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_database():
    logger.info("Dropping all tables using CASCADE...")
    async with engine.begin() as conn:
        # Postgres specific cascade drop
        await conn.execute(Base.metadata.schema_visitor(Base.metadata, "text", "drop")) # This is complex, let's use raw SQL
        await conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"))
    
    logger.info("Initializing fresh database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        await create_initial_data(session)
    
    logger.info("Database reset and seeding complete.")

if __name__ == "__main__":
    asyncio.run(reset_database())
