from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.models import ApprovalRequest, Project, Task


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.flush()
        return project

    async def list(self) -> list[Project]:
        result = await self.db.execute(select(Project).order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    async def get(self, project_id: UUID) -> Project | None:
        return await self.db.get(Project, project_id)

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task: Task) -> Task:
        self.db.add(task)
        await self.db.flush()
        return task

    async def list_for_project(self, project_id: UUID) -> list[Task]:
        result = await self.db.execute(
            select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, task_id: UUID) -> Task | None:
        return await self.db.get(Task, task_id)

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)


class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.db.add(approval)
        await self.db.flush()
        return approval

    async def list(self) -> list[ApprovalRequest]:
        result = await self.db.execute(select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc()))
        return list(result.scalars().all())

    async def get(self, approval_id: UUID) -> ApprovalRequest | None:
        return await self.db.get(ApprovalRequest, approval_id)
