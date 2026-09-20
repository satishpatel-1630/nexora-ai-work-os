from datetime import datetime
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field,AliasChoices
from apps.api.app.db.models import ApprovalStatus,ProjectStatus,RiskLevel,TaskStatus
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=200); description:str|None=None; metadata:dict=Field(default_factory=dict)
class ProjectRead(ProjectCreate):
    model_config=ConfigDict(from_attributes=True,validate_by_name=True,validate_by_alias=True)
    id:UUID; status:ProjectStatus; created_at:datetime; updated_at:datetime
    metadata:dict=Field(validation_alias=AliasChoices("metadata","metadata_json"))
class TaskCreate(BaseModel): title:str=Field(min_length=1,max_length=240); description:str|None=None; priority:int=Field(default=0,ge=0); metadata:dict=Field(default_factory=dict)
class TaskRead(TaskCreate):
    model_config=ConfigDict(from_attributes=True,validate_by_name=True,validate_by_alias=True)
    id:UUID; project_id:UUID; status:TaskStatus; created_at:datetime; updated_at:datetime
    metadata:dict=Field(validation_alias=AliasChoices("metadata","metadata_json"))
class ApprovalRead(BaseModel):
    model_config=ConfigDict(from_attributes=True,validate_by_name=True,validate_by_alias=True)
    id:UUID; action:str; target:str; reason:str; risk_level:RiskLevel; status:ApprovalStatus; proposed_changes:dict; estimated_cost:float|None; preview:dict
    metadata:dict=Field(validation_alias=AliasChoices("metadata","metadata_json")); created_at:datetime; resolved_at:datetime|None
