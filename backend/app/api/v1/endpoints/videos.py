"""
Video Production API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.video import VideoJob, VideoJobStatus
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/jobs")
async def list_video_jobs(
    status: Optional[VideoJobStatus] = None,
    script_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List video production jobs."""
    query = select(VideoJob)
    
    if status:
        query = query.where(VideoJob.status == status)
    if script_id:
        query = query.where(VideoJob.script_id == script_id)
    
    query = query.order_by(desc(VideoJob.created_at))
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [job.to_dict() for job in jobs]


@router.get("/jobs/{job_id}")
async def get_video_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get video job details."""
    result = await db.execute(
        select(VideoJob).where(VideoJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    return {
        **job.to_dict(),
        "stage_progress": job.stage_progress,
        "error_message": job.error_message,
    }


@router.post("/jobs")
async def create_video_job(
    script_id: UUID,
    priority: int = 0,
    resolution: str = "1920x1080",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Create video production job."""
    from app.models.script import Script
    
    result = await db.execute(
        select(Script).where(Script.id == script_id)
    )
    script = result.scalar_one_or_none()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    if script.status != "approved":
        raise HTTPException(status_code=400, detail="Script must be approved before video production")
    
    job = VideoJob(
        script_id=script_id,
        priority=priority,
        resolution=resolution,
        created_by=current_user.id,
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job.to_dict()


@router.post("/jobs/{job_id}/cancel")
async def cancel_video_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Cancel video job."""
    result = await db.execute(
        select(VideoJob).where(VideoJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    if job.status in [VideoJobStatus.COMPLETED, VideoJobStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed job")
    
    job.status = VideoJobStatus.CANCELLED
    await db.commit()
    
    return {"message": "Job cancelled", "job": job.to_dict()}


@router.get("/pipeline/status")
async def get_pipeline_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get video pipeline status."""
    result = await db.execute(select(VideoJob))
    jobs = result.scalars().all()
    
    return {
        "total_jobs": len(jobs),
        "queued": sum(1 for j in jobs if j.status == VideoJobStatus.QUEUED),
        "processing": sum(1 for j in jobs if j.status == VideoJobStatus.PROCESSING),
        "completed": sum(1 for j in jobs if j.status == VideoJobStatus.COMPLETED),
        "failed": sum(1 for j in jobs if j.status == VideoJobStatus.FAILED),
    }
