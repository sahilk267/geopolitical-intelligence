import httpx
import asyncio
from urllib.parse import quote

async def test():
    # Test 1: Picsum (random high-quality photos)
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            r = await c.get("https://picsum.photos/1080/1920")
            ct = r.headers.get("content-type", "unknown")
            print(f"Picsum: Status={r.status_code}, Len={len(r.content)}, Type={ct}")
    except Exception as e:
        print(f"Picsum FAIL: {e}")

    # Test 2: Unsplash Source (keyword-based)
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            r = await c.get("https://source.unsplash.com/1080x1920/?military,conflict")
            ct = r.headers.get("content-type", "unknown")
            print(f"Unsplash: Status={r.status_code}, Len={len(r.content)}, Type={ct}")
    except Exception as e:
        print(f"Unsplash FAIL: {e}")

    # Test 3: Lorem Picsum with specific seed
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            r = await c.get("https://picsum.photos/seed/conflict/1080/1920")
            ct = r.headers.get("content-type", "unknown")
            print(f"Picsum Seed: Status={r.status_code}, Len={len(r.content)}, Type={ct}")
    except Exception as e:
        print(f"Picsum Seed FAIL: {e}")

asyncio.run(test())
