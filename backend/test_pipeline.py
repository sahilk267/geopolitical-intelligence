import asyncio
import json
from app.db.base import AsyncSessionLocal
from app.services.pipeline_service import pipeline_service
async def run():
    async with AsyncSessionLocal() as db:
        res = await pipeline_service.run_full_pipeline(db, 'Conflict', 'Global')
        print(json.dumps(res))

asyncio.run(run())
