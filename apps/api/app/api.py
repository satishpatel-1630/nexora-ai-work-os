from uuid import UUID
from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.base import get_db
from apps.api.app.db.models import ApprovalStatus
from apps.api.app.schemas import ApprovalRead,ProjectCreate,ProjectRead,TaskCreate,TaskRead
from apps.api.app.services import ApprovalService,ProjectService
router=APIRouter(prefix="/api/v1")
@router.get("")
async def api_root(): return {"name":"NEXORA","status":"foundation","version":"0.1.0"}
@router.post("/projects",response_model=ProjectRead,status_code=status.HTTP_201_CREATED)
async def create_project(data:ProjectCreate,db:AsyncSession=Depends(get_db)): return await ProjectService(db).create(data)
@router.get("/projects",response_model=list[ProjectRead])
async def list_projects(db:AsyncSession=Depends(get_db)): return await ProjectService(db).list()
@router.get("/projects/{project_id}",response_model=ProjectRead)
async def get_project(project_id:UUID,db:AsyncSession=Depends(get_db)): return await ProjectService(db).get(project_id)
@router.post("/projects/{project_id}/tasks",response_model=TaskRead,status_code=status.HTTP_201_CREATED)
async def create_task(project_id:UUID,data:TaskCreate,db:AsyncSession=Depends(get_db)): return await ProjectService(db).create_task(project_id,data)
@router.get("/projects/{project_id}/tasks",response_model=list[TaskRead])
async def list_tasks(project_id:UUID,db:AsyncSession=Depends(get_db)): return await ProjectService(db).list_tasks(project_id)
@router.get("/tasks/{task_id}",response_model=TaskRead)
async def get_task(task_id:UUID,db:AsyncSession=Depends(get_db)): return await ProjectService(db).get_task(task_id)
@router.get("/approvals",response_model=list[ApprovalRead])
async def list_approvals(db:AsyncSession=Depends(get_db)): return await ApprovalService(db).list()
@router.get("/approvals/{approval_id}",response_model=ApprovalRead)
async def get_approval(approval_id:UUID,db:AsyncSession=Depends(get_db)): return await ApprovalService(db).get(approval_id)
@router.post("/approvals/{approval_id}/approve",response_model=ApprovalRead)
async def approve(approval_id:UUID,db:AsyncSession=Depends(get_db)): return await ApprovalService(db).resolve(approval_id,ApprovalStatus.APPROVED)
@router.post("/approvals/{approval_id}/reject",response_model=ApprovalRead)
async def reject(approval_id:UUID,db:AsyncSession=Depends(get_db)): return await ApprovalService(db).resolve(approval_id,ApprovalStatus.REJECTED)
