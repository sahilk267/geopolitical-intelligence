import asyncio
import httpx
from urllib.parse import quote

async def test():
    urls = [
        "https://loremflickr.com/1080/1920/military,conflict",
        "https://loremflickr.com/1080/1920/israel",
        "https://loremflickr.com/1080/1920/india,news"
    ]
    
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
        for url in urls:
            try:
                r = await c.get(url)
                print(f"{url} -> Status: {r.status_code}, Len: {len(r.content)}")
            except Exception as e:
                print(f"{url} -> Error: {e}")

asyncio.run(test())
