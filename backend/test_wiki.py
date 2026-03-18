import asyncio
import httpx
from urllib.parse import quote

async def get_wikimedia_image(query: str):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={quote(query)}"
    
    # Or search for pages:
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(query)}&format=json"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 1. Search for best article match
        res = await client.get(search_url)
        data = res.json()
        if not data.get("query", {}).get("search"):
            return None
        title = data["query"]["search"][0]["title"]
        
        # 2. Get main image for that article
        img_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={quote(title)}"
        res2 = await client.get(img_url)
        data2 = res2.json()
        pages = data2.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "original" in page_data:
                return page_data["original"]["source"]
    return None

async def test():
    img1 = await get_wikimedia_image("Israel military")
    print(f"Israel military: {img1}")
    img2 = await get_wikimedia_image("Indian Army")
    print(f"Indian Army: {img2}")

asyncio.run(test())
