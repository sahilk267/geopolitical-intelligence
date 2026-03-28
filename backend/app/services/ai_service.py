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
        self._init_provider()

    def _init_provider(self):
        """Initialize the configured LLM provider."""
        if settings.AI_PROVIDER == "gemini":
            self._init_gemini()
        else:
            self.model = None

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

    async def _ollama_generate(self, prompt: str, json_format: bool = False, model: Optional[str] = None) -> str:
        """Call Ollama generation API with retry logic."""
        import asyncio
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        model_name = model or settings.OLLAMA_MODEL
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        # Disabled 'format: json' for better speed/reliability on low-resource hosts
        # The service will use regex to extract the JSON object from the response.
        pass
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Ollama Call {attempt+1}/{max_retries}: {model_name}")
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    return response.json().get("response", "")
            except Exception as e:
                logger.warning(f"Ollama attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Ollama failed after {max_retries} attempts")
                    raise e
                await asyncio.sleep(2 ** attempt)
        return ""

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
CRITICAL REQUIREMENT: The final sentence MUST be an engaging Call to Action (CTA) asking the viewer a question to drive comments (e.g., "What do you think about this? Let us know below!").

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
Create a structured multi-scene video script for a high-end geopolitical news documentary.

Headline: {headline}
Content: {content}

Return a JSON object with this EXACT structure:
{{
  "title": "Short catchy title",
  "sentiment": "tense/hopeful/stable",
  "hashtags": ["#tag1", "#tag2", ...],
  "scenes": [
    {{
      "id": 1,
      "voiceover": "Narration for this 5-8 second scene",
      "visual_keywords": "3-4 keywords for image search (e.g., 'military tank, border, sunset')",
      "overlay_text": "Brief text to show on screen",
      "duration_seconds": 6
    }},
    ... (add 5-7 scenes covering the full report)
  ]
}}

Guidelines:
- Each voiceover should be 1-2 punchy sentences.
- Visual keywords should be descriptive for image retrieval.
- Overlay text should be a catchy headline for that specific scene.
- Ensure the narration flow is natural across scenes.

Return ONLY valid JSON."""

    async def generate_hashtags(self, text: str) -> List[str]:
        """Generate 7 viral, relevant hashtags for this news report."""
        prompt = f"Generate 7 viral, relevant hashtags for this news report. Return ONLY a JSON list of strings.\n\nReport: {text[:1000]}"
        try:
            if settings.AI_PROVIDER == "ollama":
                res = await self._ollama_generate(prompt, json_format=True)
            else:
                res = await self._gemini_generate(prompt)
            match = re.search(r"\[.*\]", res, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return [tag.strip() for tag in res.split() if tag.startswith("#")][:7]
        except Exception:
            return ["#geopolitics", "#news", "#worldnews"]

    async def generate_script(self, article_data: Dict[str, Any], layers: List[str], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a structured video script from article data with proper segments."""
        persona_name = profile.get("name", "geopolitical news channel") if profile else "geopolitical news channel"
        headline = article_data.get('headline', article_data.get('title', 'News Report'))
        content = article_data.get('content', article_data.get('summary', ''))[:1500] # Aggressive truncation for stability
        
        prompt = f"""You are a professional video script writer.
Create a structured multi-scene video script for a high-end geopolitical news documentary.

Headline: {headline}
Content: {content}

CRITICAL: Return ONLY a valid JSON object. No preamble, no markdown fences, no conversational filler.

REQUIRED JSON STRUCTURE:
{{
  "title": "Short catchy title",
  "sentiment": "tense/hopeful/stable",
  "hashtags": ["#tag1", "#tag2"],
  "scenes": [
    {{
      "id": 1,
      "voiceover": "1-2 sentences of narration",
      "visual_keywords": "3-4 keywords for img search",
      "overlay_text": "Catchy headline for scene",
      "duration_seconds": 6
    }}
  ]
}}
(Produce 5-7 scenes total)"""

        try:
            if settings.AI_PROVIDER == "ollama":
                # Use llama3.2 for speed and stability
                text = await self._ollama_generate(prompt, json_format=True, model="llama3.2")
            else:
                text = await self._gemini_generate(prompt)
                text = text.strip()
            
            # Extract JSON if LLM added text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)
            
            result = json.loads(text)
            
            if "scenes" in result:
                total_words = 0
                for scene in result["scenes"]:
                    words = len(scene.get("voiceover", "").split())
                    scene["word_count"] = words
                    total_words += words
                    if "duration_seconds" not in scene:
                        scene["duration_seconds"] = max(5, int(words / 150 * 60))
                result["total_word_count"] = total_words
                result["total_duration_seconds"] = sum(
                    s.get("duration_seconds", 0) for s in result["scenes"]
                )
            
            return result

        except Exception as e:
            logger.error(f"Error generating script: {e}. Raw output: {text[:500] if 'text' in locals() else 'None'}")
            # Resilient high-quality fallback (3 scenes)
            return {
                "title": headline,
                "sentiment": "tense",
                "hashtags": ["#Geopolitics", "#GlobalConflict", "#BreakingNews"],
                "scenes": [
                    {
                        "id": 1, 
                        "voiceover": f"Breaking news: {headline}. The situation is escalating as global powers monitor the region.", 
                        "visual_keywords": "military, headquarters, dark", 
                        "overlay_text": "INTELLIGENCE REPORT: ESCALATION", 
                        "duration_seconds": 8
                    },
                    {
                        "id": 2, 
                        "voiceover": "Strategic analysts point to shift in geopolitical dynamics. Diplomatic efforts are underway but tensions remain high.", 
                        "visual_keywords": "world map, data, connections", 
                        "overlay_text": "GLOBAL STRATEGIC SHIFT", 
                        "duration_seconds": 9
                    },
                    {
                        "id": 3, 
                        "voiceover": "Stay tuned for further updates on this developing story as we track the implications for global stability.", 
                        "visual_keywords": "city, skyline, surveillance", 
                        "overlay_text": "@StrategicContext LIVE", 
                        "duration_seconds": 7
                    }
                ]
            }


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

        # 2. Fallback to LoremFlickr (Context-aware stock photos)
        # Extract 2 main keywords from the prompt for relevance
        import re
        import hashlib
        words = re.findall(r'\b[a-zA-Z]{4,}\b', prompt.lower())
        stop_words = {'generate', 'image', 'showing', 'about', 'with', 'that', 'this', 'cinematic', 'wide', 'shot'}
        keywords = [w for w in words if w not in stop_words][:2]
        keyword_str = ",".join(keywords) if keywords else "news,world"
        
        # Use hash as random seed to avoid caching identical images
        seed = hashlib.md5(prompt.encode()).hexdigest()[:8]
        url = f"https://loremflickr.com/1080/1920/{keyword_str}?lock={int(seed, 16) % 10000}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200 and len(response.content) > 5000:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Generated fallback image via LoremFlickr for keywords: {keyword_str}")
                    return output_path
            return None
        except Exception as e:
            logger.error(f"LoremFlickr image generation failed: {e}")
            return None


ai_service = AIService()
