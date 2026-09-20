from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.models import (
    ApprovalRequest,
    ApprovalStatus,
    Event,
    Project,
    Task,
)
from apps.api.app.repositories import ApprovalRepository, ProjectRepository, TaskRepository
from apps.api.app.schemas import (
    ApprovalCreate,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
)


class NotFoundError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.projects = ProjectRepository(db)
        self.tasks = TaskRepository(db)

    async def create(self, data: ProjectCreate):
        project = Project(
            name=data.name,
            description=data.description,
            metadata_json=data.metadata,
        )
        await self.projects.create(project)
        self.db.add(Event(event_type="PROJECT_CREATED", project_id=project.id, payload={"name": project.name}))
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def list(self):
        return await self.projects.list()

    async def get(self, project_id: UUID):
        project = await self.projects.get(project_id)
        if project is None:
            raise NotFoundError("PROJECT_NOT_FOUND", "Project was not found.")
        return project

    async def update(self, project_id: UUID, data: ProjectUpdate):
        project = await self.get(project_id)
        for field in ("name", "description", "status", "metadata"):
            value = getattr(data, field)
            if value is not None:
                setattr(project, "metadata_json" if field == "metadata" else field, value)
        self.db.add(Event(event_type="PROJECT_UPDATED", project_id=project.id, payload={"project_id": str(project.id)}))
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: UUID):
        project = await self.get(project_id)
        await self.projects.delete(project)
        await self.db.commit()

    async def create_task(self, project_id: UUID, data: TaskCreate):
        await self.get(project_id)
        task = Task(
            project_id=project_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            metadata_json=data.metadata,
        )
        await self.tasks.create(task)
        self.db.add(Event(event_type="TASK_CREATED", project_id=project_id, task_id=task.id, payload={"title": task.title}))
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def list_tasks(self, project_id: UUID):
        await self.get(project_id)
        return await self.tasks.list_for_project(project_id)

    async def get_task(self, task_id: UUID):
        task = await self.tasks.get(task_id)
        if task is None:
            raise NotFoundError("TASK_NOT_FOUND", "Task was not found.")
        return task

    async def update_task(self, task_id: UUID, data: TaskUpdate):
        task = await self.get_task(task_id)
        for field in ("title", "description", "priority", "status", "metadata"):
            value = getattr(data, field)
            if value is not None:
                setattr(task, "metadata_json" if field == "metadata" else field, value)
        self.db.add(
            Event(
                event_type="TASK_STARTED" if data.status and str(data.status) == "in_progress" else "TASK_UPDATED",
                project_id=task.project_id,
                task_id=task.id,
                payload={"task_id": str(task.id)},
            )
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: UUID):
        task = await self.get_task(task_id)
        await self.tasks.delete(task)
        await self.db.commit()


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.approvals = ApprovalRepository(db)

    async def create(self, data: ApprovalCreate):
        approval = ApprovalRequest(
            action=data.action,
            target=data.target,
            reason=data.reason,
            risk_level=data.risk_level,
            proposed_changes=data.proposed_changes,
            estimated_cost=data.estimated_cost,
            preview=data.preview,
            metadata_json=data.metadata,
        )
        await self.approvals.create(approval)
        self.db.add(
            Event(
                event_type="APPROVAL_REQUESTED",
                payload={"approval_id": str(approval.id), "action": approval.action},
            )
        )
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def list(self):
        return await self.approvals.list()

    async def get(self, approval_id: UUID):
        approval = await self.approvals.get(approval_id)
        if approval is None:
            raise NotFoundError("APPROVAL_NOT_FOUND", "Approval request was not found.")
        return approval

    async def resolve(self, approval_id: UUID, status: ApprovalStatus):
        approval = await self.get(approval_id)
        if approval.status != ApprovalStatus.PENDING:
            raise ValueError("Only pending approvals can be resolved.")
        approval.status = status
        approval.resolved_at = datetime.now(UTC)
        self.db.add(
            Event(
                event_type="APPROVAL_GRANTED" if status == ApprovalStatus.APPROVED else "APPROVAL_REJECTED",
                payload={"approval_id": str(approval.id), "status": status.value},
            )
        )
        await self.db.commit()
        await self.db.refresh(approval)
        return approval


async def dependency_status(db, redis_client):
    out = {"postgres": "ok", "redis": "ok"}
    try:
        await db.execute(select(1))
    except Exception:
        out["postgres"] = "error"
    try:
        await redis_client.ping()
    except Exception:
        out["redis"] = "error"
    return out
