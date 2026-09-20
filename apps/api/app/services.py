from datetime import datetime,timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.models import ApprovalRequest,ApprovalStatus,Event,Project,Task
from apps.api.app.schemas import ProjectCreate,TaskCreate
class NotFoundError(Exception):
    def __init__(self,code:str,message:str): self.code=code; self.message=message
class ProjectService:
    def __init__(self,db:AsyncSession): self.db=db
    async def create(self,data:ProjectCreate):
        p=Project(name=data.name,description=data.description,metadata_json=data.metadata); self.db.add(p); await self.db.flush(); self.db.add(Event(event_type="PROJECT_CREATED",project_id=p.id,payload={"name":p.name})); await self.db.commit(); await self.db.refresh(p); return p
    async def list(self):
        r=await self.db.execute(select(Project).order_by(Project.created_at.desc())); return list(r.scalars().all())
    async def get(self,pid:UUID):
        p=await self.db.get(Project,pid)
        if p is None: raise NotFoundError("PROJECT_NOT_FOUND","Project was not found.")
        return p
    async def create_task(self,pid:UUID,data:TaskCreate):
        await self.get(pid); t=Task(project_id=pid,title=data.title,description=data.description,priority=data.priority,metadata_json=data.metadata); self.db.add(t); await self.db.flush(); self.db.add(Event(event_type="TASK_CREATED",project_id=pid,task_id=t.id,payload={"title":t.title})); await self.db.commit(); await self.db.refresh(t); return t
    async def list_tasks(self,pid:UUID):
        await self.get(pid); r=await self.db.execute(select(Task).where(Task.project_id==pid).order_by(Task.created_at.desc())); return list(r.scalars().all())
    async def get_task(self,tid:UUID):
        t=await self.db.get(Task,tid)
        if t is None: raise NotFoundError("TASK_NOT_FOUND","Task was not found.")
        return t
class ApprovalService:
    def __init__(self,db:AsyncSession): self.db=db
    async def list(self):
        r=await self.db.execute(select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())); return list(r.scalars().all())
    async def get(self,aid:UUID):
        a=await self.db.get(ApprovalRequest,aid)
        if a is None: raise NotFoundError("APPROVAL_NOT_FOUND","Approval request was not found.")
        return a
    async def resolve(self,aid:UUID,status:ApprovalStatus):
        a=await self.get(aid)
        if a.status!=ApprovalStatus.PENDING: raise ValueError("Only pending approvals can be resolved.")
        a.status=status; a.resolved_at=datetime.now(timezone.utc); self.db.add(Event(event_type="APPROVAL_GRANTED" if status==ApprovalStatus.APPROVED else "APPROVAL_REJECTED",payload={"approval_id":str(a.id),"status":status.value})); await self.db.commit(); await self.db.refresh(a); return a
async def dependency_status(db,redis_client):
    out={"postgres":"ok","redis":"ok"}
    try: await db.execute(select(1))
    except Exception: out["postgres"]="error"
    try: await redis_client.ping()
    except Exception: out["redis"]="error"
    return out
