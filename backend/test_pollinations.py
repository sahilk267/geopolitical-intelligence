import httpx
import asyncio
from urllib.parse import quote

prompt = "Cinematic wide shot of a military base"
url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=1024&height=1024&nologo=true"

async def test():
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as c:
        r = await c.get(url)
        ct = r.headers.get("content-type", "unknown")
        print(f"Status: {r.status_code}, Len: {len(r.content)}, Type: {ct}")

asyncio.run(test())
