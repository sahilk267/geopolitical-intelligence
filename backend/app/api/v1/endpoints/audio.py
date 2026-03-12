"""
Audio Generation API Endpoints
Generates audio from scripts using Text-to-Speech engines.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.script import Script
from app.api.v1.endpoints.auth import get_current_active_user
from app.services.tts_service import tts_service

router = APIRouter()


@router.post("/generate")
async def generate_audio(
    script_id: UUID,
    voice_id: str = "default",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Generate audio from a script using TTS."""
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    # Get the full script text
    text = script.full_script
    if not text and script.segments:
        # Concatenate segment contents
        text = " ".join(
            seg.get("content", "") for seg in script.segments if seg.get("content")
        )

    if not text:
        raise HTTPException(status_code=400, detail="Script has no content to convert to audio")

    audio_result = await tts_service.generate_audio(text, voice_id)

    if "error" in audio_result:
        raise HTTPException(status_code=500, detail=audio_result["error"])

    return {
        "script_id": str(script_id),
        "audio_url": audio_result["url"],
        "duration_seconds": audio_result["duration_seconds"],
        "file_size": audio_result["file_size"],
        "engine": audio_result["engine"],
    }


@router.post("/generate-segments")
async def generate_segment_audios(
    script_id: UUID,
    voice_id: str = "default",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Generate individual audio files for each script segment."""
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    if not script.segments:
        raise HTTPException(status_code=400, detail="Script has no segments")

    results = await tts_service.generate_segment_audios(script.segments, voice_id)

    errors = [r for r in results if "error" in r]
    if errors and len(errors) == len(results):
        raise HTTPException(status_code=500, detail="All segment audio generations failed")

    return {
        "script_id": str(script_id),
        "segments": results,
        "total_segments": len(results),
        "total_duration": sum(r.get("duration_seconds", 0) for r in results if "error" not in r),
    }


@router.post("/generate-from-text")
async def generate_audio_from_text(
    text: str,
    voice_id: str = "default",
    current_user=Depends(get_current_active_user),
):
    """Generate audio directly from text (without a saved script)."""
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters")

    audio_result = await tts_service.generate_audio(text, voice_id)

    if "error" in audio_result:
        raise HTTPException(status_code=500, detail=audio_result["error"])

    return audio_result


@router.get("/voices")
async def list_voices(current_user=Depends(get_current_active_user)):
    """List available TTS voices."""
    return tts_service.get_available_voices()
