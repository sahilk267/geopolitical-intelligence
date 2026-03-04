import google.generativeai as genai
from typing import List, Optional, Dict, Any
from app.core.config import settings
import structlog
import httpx
from bs4 import BeautifulSoup
import re

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.LLM_MODEL)
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")

    async def get_content_from_url(self, url: str) -> Dict[str, str]:
        """Scrape content from a given URL."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to get the main content
                # Common news site selectors
                headline = ""
                title_tag = soup.find('h1') or soup.find('title')
                if title_tag:
                    headline = title_tag.get_text().strip()
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing whitespace
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Limit text size for Gemini
                clean_text = text[:10000] 
                
                return {
                    "headline": headline,
                    "content": clean_text
                }
        except Exception as e:
            logger.error("Scraping error", url=url, error=str(e))
            return {"error": str(e)}

    async def summarize_article(self, headline: str, content: str) -> str:
        """Summarize article content using Gemini."""
        if not self.model:
            return "AI Summarization is currently disabled (API key missing)."
        
        prompt = f"Summarize the following geopolitical news article in 3-4 concise sentences:\n\nHeadline: {headline}\nContent: {content}"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error("Error generating summary with Gemini", error=str(e))
            return f"Error generating summary: {str(e)}"

    async def generate_script(self, article_data: Dict[str, Any], layers: List[str]) -> Dict[str, Any]:
        """Generate a video script from article data."""
        if not self.model:
            return {"error": "AI Script Generation is currently disabled (API key missing)."}

        prompt = f"""
        Generate a professional news video script for the following topic:
        Headline: {article_data.get('headline')}
        Summary: {article_data.get('summary')}
        
        Layers requested: {', '.join(layers)}
        
        Format the output as a JSON object with:
        - "title": Title of the video
        - "segments": A list of objects with "type" (intro, facts, analysis, scenario, closing), "content" (the spoken text), and "visual_hint" (what should be shown on screen).
        """
        
        try:
            response = self.model.generate_content(prompt)
            # In production, we would parse JSON. For now, returning text or basic structure.
            return {
                "full_script": response.text,
                "segments": [{"type": "generated", "content": response.text}]
            }
        except Exception as e:
            logger.error("Error generating script with Gemini", error=str(e))
            return {"error": str(e)}

ai_service = AIService()
