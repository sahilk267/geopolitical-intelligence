"""
Migration: Add category and region columns to raw_articles table
Run this script once to update an existing database.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.db.base import engine


async def migrate():
    """Add category and region columns to raw_articles if they don't exist."""
    async with engine.begin() as conn:
        print("Adding 'category' column to raw_articles...")
        await conn.execute(text(
            "ALTER TABLE raw_articles ADD COLUMN IF NOT EXISTS category VARCHAR(100)"
        ))
        
        print("Adding 'region' column to raw_articles...")
        await conn.execute(text(
            "ALTER TABLE raw_articles ADD COLUMN IF NOT EXISTS region VARCHAR(100)"
        ))
        
        print("Migration completed successfully!")


async def rollback():
    """Remove category and region columns (if needed)."""
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE raw_articles DROP COLUMN IF EXISTS category"))
        await conn.execute(text("ALTER TABLE raw_articles DROP COLUMN IF EXISTS region"))
        print("Rollback completed.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "migrate"
    if action == "rollback":
        asyncio.run(rollback())
    else:
        asyncio.run(migrate())
