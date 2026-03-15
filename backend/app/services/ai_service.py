"""
AI Service - Geopolitical Intelligence Platform
Provides journalist-quality summarization, report generation, and script creation
using Google Gemini API.
"""
import google.generativeai as genai
from typing import List, Optional, Dict, Any
from app.core.config import settings
import structlog
import httpx
from bs4 import BeautifulSoup
import re
import json

# RAG (Persona Memory)
try:
    from app.services.rag_service import rag_service
    _rag_available = True
except ImportError:
    _rag_available = False

logger = structlog.get_logger()


class AIService:
    def __init__(self):
        self._init_gemini()

    def _init_gemini(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.LLM_MODEL)
        else:
            self.model = None

    async def _gemini_generate(self, prompt: str) -> str:
        """Async wrapper for Gemini generation."""
        if not self.model:
            return "Gemini API key not configured."
        # generate_content is synchronous in the current SDK, wrapping in thread if needed
        # but for now we'll call it directly as it's usually fast enough for low concurrency
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise e

    async def _ollama_generate(self, prompt: str, json_format: bool = False) -> str:
        """Call Ollama generation API."""
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.LLM_TEMPERATURE
            }
        }
        if json_format:
            payload["format"] = "json"
            
        logger.info(f"DEBUG: Calling Ollama at {url} with model {payload['model']}")
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                raise e

    # ──────────────────────────────────────────────
    # URL SCRAPING
    # ──────────────────────────────────────────────

    async def get_content_from_url(self, url: str) -> Dict[str, str]:
        """Scrape content from a given URL."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract headline
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
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
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

    # ──────────────────────────────────────────────
    # BASIC SUMMARIZATION (Single Article)
    # ──────────────────────────────────────────────

    async def summarize_article(self, headline: str, content: str) -> str:
        """Summarize article content using Gemini."""
        prompt = f"""You are a senior geopolitical analyst. Summarize this article concisely in 3-5 sentences, focusing on geopolitical implications.

Headline: {headline}

Content: {content[:5000]}

Provide a clear, analytical summary:"""
        try:
            if settings.AI_PROVIDER == "ollama":
                return await self._ollama_generate(prompt, json_format=False)
            else:
                if not self.model:
                    return "AI Summarization is currently disabled (API key missing)."
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error("Error generating summary", error=str(e))
            return f"Error generating summary: {str(e)}"

    # ──────────────────────────────────────────────
    # JOURNALIST REPORT (Multi-Article, Category-Based)
    # ──────────────────────────────────────────────

    async def generate_journalist_report(
        self,
        articles: List[Dict[str, Any]],
        category: str,
        region: str = "Global",
        profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a journalist-quality intelligence report from multiple articles.
        Mimics the style of a top-tier geopolitical analyst/journalist or a specific persona.
        """
        # Build persona context
        persona_context = ""
        if profile:
            persona_context = f"Write this in the style of '{profile.get('name')}': {profile.get('description', '')}"
        else:
            persona_context = "You are a senior geopolitical intelligence analyst writing for a top-tier publication."

        # RAG: Recall relevant past analyses for this persona
        memory_context = ""
        profile_id = profile.get("id", "") if profile else ""
        if _rag_available and profile_id:
            try:
                query = f"{category} {region} geopolitical analysis"
                memories = await rag_service.recall(str(profile_id), query, top_k=3)
                if memories:
                    memory_snippets = [m["text"] for m in memories]
                    memory_context = "\n\nYOUR PAST ANALYSES (use these for deeper insight and continuity):\n" + "\n---\n".join(memory_snippets)
            except Exception as e:
                logger.warning(f"RAG recall failed: {e}")

        # Build article summaries for the prompt
        article_texts = []
        for i, art in enumerate(articles[:10], 1):
            title = art.get('title') or 'Untitled'
            content = (art.get('content') or art.get('summary') or '')[:1500]
            article_texts.append(f"Article {i}: {title}\n{content}")
        
        articles_block = "\n\n".join(article_texts)
        
        prompt = f"""{persona_context}{memory_context}
Analyze the following {len(articles)} articles about {category} (Region: {region}) and produce a structured intelligence report.

ARTICLES:
{articles_block}

Return a JSON object with this exact structure:
{{
  "headline": "A compelling, journalist-quality headline",
  "executive_summary": "A 2-3 paragraph executive summary of the key developments",
  "key_developments": ["Development 1", "Development 2", "Development 3"],
  "analysis": "Deep analytical paragraph connecting the dots between events",
  "outlook": "Forward-looking assessment of what may happen next",
  "risk_level": "LOW|MODERATE|ELEVATED|HIGH|CRITICAL",
  "tags": ["tag1", "tag2"]
}}

Return ONLY valid JSON, no markdown fences or extra text."""

        try:
            if settings.AI_PROVIDER == "ollama":
                text = await self._ollama_generate(prompt, json_format=True)
            else:
                text = await self._gemini_generate(prompt)
                text = text.strip()
            
            if not text:
                return {"error": "AI provider returned empty response"}

            # Clean potential markdown code fences
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
            
            try:
                report = json.loads(text)
            except json.JSONDecodeError as jde:
                logger.warning(f"JSON decode failed for {settings.AI_PROVIDER}")
                report = {
                    "headline": f"{category} Intelligence Report",
                    "executive_summary": text,
                    "key_developments": [],
                    "analysis": "Manual parsing required due to non-JSON output.",
                    "outlook": "",
                    "risk_level": "MODERATE",
                    "tags": [category, region],
                }

            # RAG: Store the generated report in persona memory
            if _rag_available and profile_id:
                try:
                    summary = report.get("executive_summary", "")
                    analysis = report.get("analysis", "")
                    memory_text = f"{report.get('headline', '')}\n{summary}\n{analysis}"
                    await rag_service.store_memory(
                        str(profile_id), memory_text,
                        metadata={"category": category, "region": region}
                    )
                except Exception as e:
                    logger.warning(f"RAG store failed: {e}")

            return report
            
        except Exception as e:
            logger.error(f"Error in generate_journalist_report: {str(e)}")
            return {"error": str(e)}

    # ──────────────────────────────────────────────
    # SHORT SUMMARY (30-second narration for clips)
    # ──────────────────────────────────────────────

    async def generate_short_summary(self, headline: str, content: str, profile: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate a 30-second narration script for short clips."""
        persona_style = profile.get("name", "Broadcast News Writer") if profile else "Broadcast News Writer"
        content_text = (content or "")[:2000]
        prompt = f"""You are a {persona_style}. Create a 30-second narration script (approximately 75 words) for a short video clip.
The script should be punchy, engaging, and authoritative.

Topic: {headline}
Content: {content_text}
"""
        try:
            if settings.AI_PROVIDER == "ollama":
                text = await self._ollama_generate(prompt, json_format=True)
            else:
                text = await self._gemini_generate(prompt)
                text = text.strip()
                
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception as e:
            logger.error("Error generating short summary", error=str(e))
            return {"error": str(e)}

    # ──────────────────────────────────────────────
    # FULL VIDEO SCRIPT (Presenter narration)
    # ──────────────────────────────────────────────

    async def generate_script(self, article_data: Dict[str, Any], layers: List[str], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a structured video script from article data with proper segments."""
        persona_name = profile.get("name", "geopolitical news channel") if profile else "geopolitical news channel"
        headline = article_data.get('headline', article_data.get('title', 'News Report'))
        content = article_data.get('content', article_data.get('summary', ''))[:5000]
        layers_str = ', '.join(layers) if layers else 'narration'
        
        prompt = f"""You are a professional video script writer for a {persona_name}.
Create a structured video script for a presenter-style news segment.

Headline: {headline}
Content: {content}
Required layers: {layers_str}

Return a JSON object:
{{
  "title": "Script title",
  "segments": [
    {{
      "type": "intro",
      "content": "Opening narration text (2-3 sentences)",
      "visual_notes": "Description of visuals for this segment"
    }},
    {{
      "type": "body",
      "content": "Main body narration (3-5 sentences)",
      "visual_notes": "Description of visuals"
    }},
    {{
      "type": "analysis",
      "content": "Analysis narration (2-3 sentences)",
      "visual_notes": "Description of visuals"
    }},
    {{
      "type": "closing",
      "content": "Closing narration (1-2 sentences)",
      "visual_notes": "Description of visuals"
    }}
  ]
}}

Return ONLY valid JSON."""

        try:
            if settings.AI_PROVIDER == "ollama":
                text = await self._ollama_generate(prompt, json_format=True)
            else:
                text = await self._gemini_generate(prompt)
                text = text.strip()
            
            # Clean potential markdown code fences
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
            
            result = json.loads(text)
            
            # Calculate word counts if not provided
            if "segments" in result:
                total_words = 0
                for segment in result["segments"]:
                    words = len(segment.get("content", "").split())
                    segment["word_count"] = words
                    total_words += words
                    if "estimated_duration_seconds" not in segment:
                        segment["estimated_duration_seconds"] = int(words / 150 * 60)
                result["total_word_count"] = total_words
                result["total_duration_seconds"] = sum(
                    s.get("estimated_duration_seconds", 0) for s in result["segments"]
                )
            
            return result

        except json.JSONDecodeError:
            logger.warning(f"{settings.AI_PROVIDER} returned non-JSON for script, wrapping")
            full_text = text if 'text' in locals() else ""
            return {
                "title": article_data.get("headline", "Generated Script"),
                "full_script": full_text,
                "segments": [{"type": "generated", "content": full_text}],
                "total_word_count": len(full_text.split()),
                "total_duration_seconds": int(len(full_text.split()) / 150 * 60) if full_text else 0,
            }
        except Exception as e:
            logger.error("Error generating script", error=str(e))
            return {"error": str(e)}


    async def generate_image_prompts(self, report_text: str) -> List[str]:
        """
        Generate 3-5 visual image prompts based on a news report.
        """
        prompt = f"""
        Analyze the following news report and create 3 distinct visual image prompts for cinematic B-roll.
        Style requirements: Cinematic, hyper-realistic, 8k resolution, dramatic lighting, news photography style.
        The prompts should be highly descriptive and relevant to the geopolitical theme.
        Avoid text, people's faces (keep them symbolic or silhouetted), and logos.
        Focus on: Architecture, technology, military assets, maps, urban landscapes, or symbolic objects.
        
        Report: {report_text[:2000]}
        
        Respond with ONLY a JSON list of strings.
        Example: ["Cinematic wide shot of a high-tech server room with pulsating blue fiber optic cables, dramatic shadows, 8k", "Close-up of a drone flying over a vast, arid desert landscape under a setting sun, realistic, high-detail", "A glowing digital holographic world map with intricate data connections between major cities, dark background, cinematic"]
        """

        try:
            if settings.AI_PROVIDER == "ollama":
                response = await self._ollama_generate(prompt)
            else:
                response = await self._gemini_generate(prompt)

            # Extract JSON list
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return [line.strip("- ") for line in response.strip().split("\n") if line.strip()][:3]
        except Exception as e:
            logger.error(f"Error generating image prompts: {e}")
            return ["A cinematic world map with data connections", "Abstract digital intelligence visualization"]

    async def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Fetch an image. Priority:
        1. Local Stable Diffusion API (SD.Next / A1111) if configured
        2. Free Cloud API (Pollinations.ai) as fallback
        """
        import httpx
        from urllib.parse import quote
        
        # 1. Try Local Stable Diffusion (DirectML/CUDA) with Retry Logic
        if settings.STABLE_DIFFUSION_URL:
            import asyncio
            sd_api_url = f"{settings.STABLE_DIFFUSION_URL.rstrip('/')}/sdapi/v1/txt2img"
            payload = {
                "prompt": prompt,
                "negative_prompt": "text, logo, watermark, blurry, low quality, distorted",
                "steps": 20,
                "width": 1024,
                "height": 1024,
                "cfg_scale": 7,
                "sampler_name": "Euler a"
            }
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(sd_api_url, json=payload)
                        if response.status_code == 200:
                            import base64
                            data = response.json()
                            if "images" in data and len(data["images"]) > 0:
                                image_data = base64.b64decode(data["images"][0])
                                with open(output_path, "wb") as f:
                                    f.write(image_data)
                                logger.info(f"Generated local image via DirectML SD for: {prompt[:50]}...")
                                return output_path
                        else:
                            logger.warning(f"SD.Next returned status {response.status_code} on attempt {attempt+1}")
                except Exception as e:
                    logger.debug(f"Local Stable Diffusion attempt {attempt+1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
            logger.warning("All SD.Next retry attempts failed, falling back to cloud.")

        # 2. Fallback to Pollinations.ai (Free Cloud)
        encoded_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Generated cloud image via Pollinations.ai for: {prompt[:50]}...")
                    return output_path
            return None
        except Exception as e:
            logger.error(f"Cloud image generation failed for '{prompt}': {e}")
            return None


ai_service = AIService()
