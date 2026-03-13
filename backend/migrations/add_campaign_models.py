"""
Migration: Add profiles and campaigns tables
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.db.base import engine


async def migrate():
    """Create profiles and campaigns tables if they don't exist."""
    async with engine.begin() as conn:
        print("Creating 'profiles' table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                voice_engine VARCHAR(50) DEFAULT 'edge-tts',
                voice_id VARCHAR(100),
                video_style JSONB DEFAULT '{}',
                platform_configs JSONB DEFAULT '{}',
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                created_by UUID REFERENCES users(id)
            )
        """))
        
        print("Creating 'campaigns' table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                profile_id UUID NOT NULL REFERENCES profiles(id),
                categories JSONB DEFAULT '[]',
                regions JSONB DEFAULT '[]',
                is_active BOOLEAN DEFAULT TRUE,
                schedule_type VARCHAR(50) DEFAULT 'daily',
                schedule_config JSONB DEFAULT '{}',
                last_run_at TIMESTAMP WITHOUT TIME ZONE,
                next_run_at TIMESTAMP WITHOUT TIME ZONE,
                history JSONB DEFAULT '[]',
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                created_by UUID REFERENCES users(id)
            )
        """))
        
        print("Migration completed successfully!")


async def rollback():
    """Drop profiles and campaigns tables."""
    async with engine.begin() as conn:
        print("Dropping 'campaigns' table...")
        await conn.execute(text("DROP TABLE IF EXISTS campaigns"))
        print("Dropping 'profiles' table...")
        await conn.execute(text("DROP TABLE IF EXISTS profiles"))
        print("Rollback completed.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "migrate"
    if action == "rollback":
        asyncio.run(rollback())
    else:
        asyncio.run(migrate())
