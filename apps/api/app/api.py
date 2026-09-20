from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
import redis.asyncio as redis
from apps.api.app.config import get_settings
from apps.api.app.contracts import Job
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.base import get_db
from apps.api.app.db.models import ApprovalStatus
from apps.api.app.schemas import (
    ApprovalCreate,
    ApprovalRead,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from apps.api.app.services import ApprovalService, ProjectService
from intelligence.persistence import create_run, get_run
from intelligence.schemas import IntelligenceRunCreate, IntelligenceRunRead



router = APIRouter(prefix="/api/v1")


@router.get("")
async def api_root():
    return {"name": "NEXORA", "status": "foundation", "version": "0.1.0"}


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).create(data)


@router.get("/projects", response_model=list[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).list()


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).get(project_id)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
async def update_project(project_id: UUID, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).update(project_id, data)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    await ProjectService(db).delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: UUID, data: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).create_task(project_id, data)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
async def list_tasks(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).list_tasks(project_id)


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).get_task(task_id)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).update_task(task_id, data)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    await ProjectService(db).delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/approvals", response_model=ApprovalRead, status_code=status.HTTP_201_CREATED)
async def create_approval(data: ApprovalCreate, db: AsyncSession = Depends(get_db)):
    return await ApprovalService(db).create(data)


@router.get("/approvals", response_model=list[ApprovalRead])
async def list_approvals(db: AsyncSession = Depends(get_db)):
    return await ApprovalService(db).list()


@router.get("/approvals/{approval_id}", response_model=ApprovalRead)
async def get_approval(approval_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ApprovalService(db).get(approval_id)


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRead)
async def approve(approval_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ApprovalService(db).resolve(approval_id, ApprovalStatus.APPROVED)


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalRead)
async def reject(approval_id: UUID, db: AsyncSession = Depends(get_db)):
    return await ApprovalService(db).resolve(approval_id, ApprovalStatus.REJECTED)


@router.post("/intelligence/runs", response_model=IntelligenceRunRead, status_code=status.HTTP_201_CREATED)
async def create_intelligence_run(data: IntelligenceRunCreate, db: AsyncSession = Depends(get_db)):
    return await create_run(db, data.request, data.project_id, data.task_id)

@router.get("/intelligence/runs", response_model=list[IntelligenceRunRead])
async def list_intelligence_runs(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import IntelligenceRun
    return list((await db.execute(select(IntelligenceRun).order_by(IntelligenceRun.created_at.desc()).limit(50))).scalars().all())

@router.get("/intelligence/runs/{run_id}", response_model=IntelligenceRunRead)
async def get_intelligence_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await get_run(db, run_id)
    if row is None:
        from apps.api.app.services import NotFoundError
        raise NotFoundError("INTELLIGENCE_RUN_NOT_FOUND", "Intelligence run was not found.")
    return row

@router.post("/intelligence/runs/{run_id}/execute", response_model=IntelligenceRunRead)
async def execute_intelligence_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await get_run(db, run_id)
    if row is None:
        from apps.api.app.services import NotFoundError
        raise NotFoundError("INTELLIGENCE_RUN_NOT_FOUND", "Intelligence run was not found.")
    client = redis.from_url(get_settings().redis_url, decode_responses=True)
    try:
        from dataclasses import asdict
        from uuid import uuid4
        job = Job(id=uuid4(), type="INTELLIGENCE_RUN", payload={"run_id": str(run_id)})
        await client.rpush("nexora:jobs", __import__("json").dumps(asdict(job), default=str))
        row.status = "pending"
        row.current_stage = "intent"
        await db.commit()
        await db.refresh(row)
        return row
    finally:
        await client.aclose()

@router.get("/intelligence/runs/{run_id}/research")
async def get_intelligence_research(run_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import ResearchFindingRecord
    return list((await db.execute(select(ResearchFindingRecord).where(ResearchFindingRecord.intelligence_run_id==run_id))).scalars().all())

@router.get("/intelligence/runs/{run_id}/plan")
async def get_intelligence_plan(run_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import TaskPlanRecord
    return (await db.execute(select(TaskPlanRecord).where(TaskPlanRecord.intelligence_run_id==run_id))).scalar_one_or_none()

@router.get("/intelligence/runs/{run_id}/briefs")
async def get_intelligence_briefs(run_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import SpecialistBriefRecord
    return list((await db.execute(select(SpecialistBriefRecord).where(SpecialistBriefRecord.intelligence_run_id==run_id))).scalars().all())

@router.get("/intelligence/runs/{run_id}/prompts")
async def get_intelligence_prompts(run_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import PromptArtifactRecord
    return list((await db.execute(select(PromptArtifactRecord).where(PromptArtifactRecord.intelligence_run_id==run_id))).scalars().all())

@router.get("/intelligence/runs/{run_id}/usage")
async def get_intelligence_usage(run_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from apps.api.app.db.models import ModelInvocation
    return list((await db.execute(select(ModelInvocation).where(ModelInvocation.intelligence_run_id==run_id))).scalars().all())
