import google.generativeai as genai
from typing import List, Optional, Dict, Any
from app.core.config import settings
import structlog

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.LLM_MODEL)
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")

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
