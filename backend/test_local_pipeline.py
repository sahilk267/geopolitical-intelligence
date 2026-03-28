"""
═══════════════════════════════════════════════════════════════════
 End-to-End Local AI Pipeline Test
 Tests: Ollama → SD.Next → SadTalker → FFmpeg → Distribution
═══════════════════════════════════════════════════════════════════
 Run: python test_local_pipeline.py
"""
import asyncio
import os
import sys
import time
import uuid
import json
import subprocess
import httpx

# ── Configuration ──────────────────────────────────────────────
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SD_NEXT_URL = os.getenv("STABLE_DIFFUSION_URL", "http://localhost:7860")
SADTALKER_DIR = os.getenv("SADTALKER_DIR", os.path.join(os.path.dirname(__file__), "..", "sadtalker"))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "test_mission")
MUSIC_PATH = os.path.join(os.path.dirname(__file__), "assets", "music", "cinematic_news.mp3")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────
def log_step(step: str, status: str, detail: str = "", elapsed: float = 0):
    icon = "✅" if status == "OK" else "❌" if status == "FAIL" else "⏳" if status == "SKIP" else "🔄"
    time_str = f" ({elapsed:.1f}s)" if elapsed else ""
    print(f"  {icon} [{step}] {status}{time_str} {detail}")


# ── Mock Article Data ──────────────────────────────────────────
MOCK_ARTICLES = [
    {
        "headline": "Rising Tensions in South China Sea as Naval Exercises Intensify",
        "content": "Multiple nations have increased naval presence in the South China Sea. "
                   "The Philippines has filed diplomatic protests, while China continues to "
                   "assert territorial claims over disputed waters. Japan and Australia have "
                   "announced joint freedom of navigation operations.",
        "source": "Reuters",
        "category": "military",
    },
    {
        "headline": "EU Imposes New Sanctions Package on Russian Energy Sector",
        "content": "The European Union has adopted its 14th sanctions package targeting "
                   "Russia's energy infrastructure. The measures include restrictions on LNG "
                   "transshipment and new prohibitions on technology transfers for oil refining.",
        "source": "Bloomberg",
        "category": "economic",
    },
    {
        "headline": "Middle East Peace Talks Resume with New Mediator Framework",
        "content": "Diplomatic efforts to resolve the ongoing Middle East conflict have "
                   "entered a new phase. Saudi Arabia and Egypt are co-hosting negotiations "
                   "with a focus on a phased ceasefire and humanitarian corridor establishment.",
        "source": "Al Jazeera",
        "category": "diplomatic",
    },
]


# ═══════════════════════════════════════════════════════════════
# STEP 1: Ollama LLM — Generate Geopolitical Report
# ═══════════════════════════════════════════════════════════════
async def test_ollama() -> dict:
    print("\n🧠 STEP 1: Testing Ollama LLM (Local Reasoning)...")
    t0 = time.time()

    prompt = f"""You are a senior geopolitical analyst. Based on these intelligence briefings, 
write a concise 3-paragraph executive summary suitable for a news broadcast narration.

Articles:
{json.dumps(MOCK_ARTICLES, indent=2)}

Respond ONLY with the narration text, no headers or labels. Keep it under 200 words."""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            report_text = resp.json().get("response", "")

        elapsed = time.time() - t0
        if not report_text or len(report_text) < 50:
            log_step("Ollama", "FAIL", "Empty or too short response")
            return {"status": "fail", "text": ""}

        log_step("Ollama", "OK", f"{len(report_text)} chars generated", elapsed)

        # Save report
        report_path = os.path.join(OUTPUT_DIR, "report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        return {"status": "ok", "text": report_text, "path": report_path}

    except Exception as e:
        log_step("Ollama", "FAIL", str(e))
        return {"status": "fail", "text": "", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# STEP 2: TTS — Convert Report to Audio
# ═══════════════════════════════════════════════════════════════
async def test_tts(report_text: str) -> dict:
    print("\n🎙️ STEP 2: Testing TTS (Text-to-Speech)...")
    t0 = time.time()

    audio_path = os.path.join(OUTPUT_DIR, "narration.mp3")

    try:
        from gtts import gTTS
        tts = gTTS(text=report_text, lang="en", slow=False)
        tts.save(audio_path)
        elapsed = time.time() - t0

        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
            log_step("TTS (gTTS)", "OK", f"{os.path.getsize(audio_path) // 1024} KB", elapsed)
            return {"status": "ok", "path": audio_path}
        else:
            log_step("TTS", "FAIL", "Output file too small or missing")
            return {"status": "fail"}

    except ImportError:
        log_step("TTS", "FAIL", "gTTS not installed. Run: pip install gtts")
        return {"status": "fail", "error": "gTTS not installed"}
    except Exception as e:
        log_step("TTS", "FAIL", str(e))
        return {"status": "fail", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# STEP 3: SD.Next — Generate B-Roll Image
# ═══════════════════════════════════════════════════════════════
async def test_sdnext() -> dict:
    print("\n🖼️ STEP 3: Testing SD.Next (Local Image Generation)...")
    t0 = time.time()

    image_path = os.path.join(OUTPUT_DIR, "broll_test.png")
    prompt = "Cinematic wide shot of a naval fleet in the South China Sea at sunset, dramatic lighting, 8k, photorealistic, news photography"

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{SD_NEXT_URL}/sdapi/v1/txt2img",
                json={
                    "prompt": prompt,
                    "negative_prompt": "blurry, text, watermark, low quality",
                    "steps": 8,
                    "width": 512,
                    "height": 512,
                    "cfg_scale": 2.0,
                    "sampler_name": "DPM++ 2M",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        import base64
        if data.get("images"):
            img_data = base64.b64decode(data["images"][0])
            with open(image_path, "wb") as f:
                f.write(img_data)
            elapsed = time.time() - t0
            log_step("SD.Next", "OK", f"{os.path.getsize(image_path) // 1024} KB image", elapsed)
            return {"status": "ok", "path": image_path}
        else:
            log_step("SD.Next", "FAIL", "No images in response")
            return {"status": "fail"}

    except httpx.ConnectError:
        log_step("SD.Next", "SKIP", "SD.Next not running at " + SD_NEXT_URL)
        return {"status": "skip", "reason": "SD.Next offline"}
    except Exception as e:
        log_step("SD.Next", "FAIL", str(e))
        return {"status": "fail", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# STEP 4: SadTalker — Generate Talking Head Video
# ═══════════════════════════════════════════════════════════════
async def test_sadtalker(audio_path: str) -> dict:
    print("\n🎭 STEP 4: Testing SadTalker (Local Avatar Generation)...")
    t0 = time.time()

    inference_script = os.path.join(SADTALKER_DIR, "inference.py")
    checkpoint_dir = os.path.join(SADTALKER_DIR, "checkpoints")
    venv_python = os.path.join(SADTALKER_DIR, "venv", "Scripts", "python.exe")
    source_image = os.path.join(SADTALKER_DIR, "examples", "source_image", "full_body_1.png")
    result_dir = os.path.join(OUTPUT_DIR, "sadtalker_out")

    if not os.path.exists(inference_script):
        log_step("SadTalker", "SKIP", f"Not installed at {SADTALKER_DIR}")
        return {"status": "skip"}

    if not os.path.exists(checkpoint_dir) or len(os.listdir(checkpoint_dir)) < 2:
        log_step("SadTalker", "SKIP", "Checkpoints missing")
        return {"status": "skip"}

    python_exe = venv_python if os.path.exists(venv_python) else "python"

    cmd = [
        python_exe, inference_script,
        "--driven_audio", os.path.abspath(audio_path),
        "--source_image", source_image,
        "--checkpoint_dir", checkpoint_dir,
        "--result_dir", result_dir,
        "--size", "256",
        "--preprocess", "crop",
        "--still",
        "--cpu",
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=SADTALKER_DIR,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)

        if process.returncode != 0:
            err = stderr.decode("utf-8", errors="replace")[-300:]
            log_step("SadTalker", "FAIL", f"Exit code {process.returncode}: {err[:100]}")
            return {"status": "fail", "error": err}

        # Find generated video
        output_video = result_dir + ".mp4"
        if os.path.exists(output_video):
            elapsed = time.time() - t0
            log_step("SadTalker", "OK", f"{os.path.getsize(output_video) // 1024} KB video", elapsed)
            return {"status": "ok", "path": output_video}
        else:
            log_step("SadTalker", "FAIL", "No output video found")
            return {"status": "fail"}

    except asyncio.TimeoutError:
        log_step("SadTalker", "FAIL", "Timed out after 10 minutes")
        return {"status": "fail", "error": "timeout"}
    except Exception as e:
        log_step("SadTalker", "FAIL", str(e))
        return {"status": "fail", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# STEP 5: FFmpeg — Mix Audio + Music
# ═══════════════════════════════════════════════════════════════
async def test_ffmpeg_mix(audio_path: str) -> dict:
    print("\n🎵 STEP 5: Testing FFmpeg (Audio + Music Mixing)...")
    t0 = time.time()

    output_path = os.path.join(OUTPUT_DIR, "mixed_audio.mp3")

    # Check for FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            raise FileNotFoundError("ffmpeg not found")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Try common Windows install paths
        ffmpeg_paths = [
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
        ]
        # Search for winget-installed ffmpeg
        import glob
        winget_paths = glob.glob(r"C:\Users\*\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe")
        ffmpeg_paths.extend(winget_paths)

        ffmpeg_exe = None
        for p in ffmpeg_paths:
            if os.path.exists(p):
                ffmpeg_exe = p
                break

        if not ffmpeg_exe:
            log_step("FFmpeg", "SKIP", "FFmpeg not found in PATH. Restart your terminal after winget install.")
            return {"status": "skip"}
    else:
        ffmpeg_exe = "ffmpeg"

    if not os.path.exists(MUSIC_PATH):
        log_step("FFmpeg", "SKIP", f"Music file not found: {MUSIC_PATH}")
        # Still OK — just copy the narration
        import shutil
        shutil.copy2(audio_path, output_path)
        return {"status": "ok", "path": output_path, "note": "No music track, copied narration only"}

    cmd = [
        ffmpeg_exe, "-y",
        "-i", audio_path,
        "-i", MUSIC_PATH,
        "-filter_complex", "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=shortest",
        "-ac", "2",
        output_path,
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        elapsed = time.time() - t0

        if proc.returncode == 0 and os.path.exists(output_path):
            log_step("FFmpeg", "OK", f"{os.path.getsize(output_path) // 1024} KB mixed audio", elapsed)
            return {"status": "ok", "path": output_path}
        else:
            log_step("FFmpeg", "FAIL", proc.stderr[:200] if proc.stderr else "Unknown error")
            return {"status": "fail"}

    except Exception as e:
        log_step("FFmpeg", "FAIL", str(e))
        return {"status": "fail", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# MAIN — Run All Steps
# ═══════════════════════════════════════════════════════════════
async def main():
    print("=" * 60)
    print("🚀 GEOPOLITICAL INTELLIGENCE — LOCAL AI PIPELINE TEST")
    print("=" * 60)
    total_start = time.time()

    results = {}

    # Step 1: LLM
    results["ollama"] = await test_ollama()

    # Step 2: TTS
    if results["ollama"]["status"] == "ok":
        results["tts"] = await test_tts(results["ollama"]["text"])
    else:
        print("\n⚠️  Skipping TTS — no report text from Ollama")
        results["tts"] = {"status": "skip"}

    # Step 3: SD.Next
    results["sdnext"] = await test_sdnext()

    # Step 4: SadTalker
    if results["tts"].get("path"):
        results["sadtalker"] = await test_sadtalker(results["tts"]["path"])
    else:
        print("\n⚠️  Skipping SadTalker — no audio from TTS")
        results["sadtalker"] = {"status": "skip"}

    # Step 5: FFmpeg
    if results["tts"].get("path"):
        results["ffmpeg"] = await test_ffmpeg_mix(results["tts"]["path"])
    else:
        print("\n⚠️  Skipping FFmpeg — no audio from TTS")
        results["ffmpeg"] = {"status": "skip"}

    # ── Summary ──
    total_time = time.time() - total_start
    print("\n" + "=" * 60)
    print("📊 PIPELINE TEST SUMMARY")
    print("=" * 60)

    for step, res in results.items():
        status = res.get("status", "unknown").upper()
        icon = "✅" if status == "OK" else "❌" if status == "FAIL" else "⏳"
        print(f"  {icon} {step.upper():15s} → {status}")

    print(f"\n  ⏱️  Total time: {total_time:.1f}s")
    print(f"  📁 Output dir:  {OUTPUT_DIR}")

    ok_count = sum(1 for r in results.values() if r.get("status") == "ok")
    total = len(results)
    print(f"\n  {'🎉' if ok_count == total else '⚠️'}  {ok_count}/{total} steps passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
