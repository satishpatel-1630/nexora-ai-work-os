from datetime import datetime
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field
from apps.api.app.db.models import ApprovalStatus,ProjectStatus,RiskLevel,TaskStatus
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=200); description:str|None=None; metadata:dict=Field(default_factory=dict)
class ProjectRead(ProjectCreate):
    model_config=ConfigDict(from_attributes=True)
    id:UUID; status:ProjectStatus; created_at:datetime; updated_at:datetime
class TaskCreate(BaseModel): title:str=Field(min_length=1,max_length=240); description:str|None=None; priority:int=Field(default=0,ge=0); metadata:dict=Field(default_factory=dict)
class TaskRead(TaskCreate):
    model_config=ConfigDict(from_attributes=True)
    id:UUID; project_id:UUID; status:TaskStatus; created_at:datetime; updated_at:datetime
class ApprovalRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:UUID; action:str; target:str; reason:str; risk_level:RiskLevel; status:ApprovalStatus; proposed_changes:dict; estimated_cost:float|None; preview:dict; metadata:dict; created_at:datetime; resolved_at:datetime|None
