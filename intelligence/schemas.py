from datetime import datetime
from uuid import UUID
from pydantic import BaseModel,Field
from .models import RunStatus, Stage
class IntelligenceRunCreate(BaseModel):
    request:str=Field(min_length=1,max_length=20000); project_id:UUID|None=None; task_id:UUID|None=None; mode:str="analyze"
class IntelligenceRunRead(BaseModel):
    id:UUID; request:str; status:RunStatus; current_stage:Stage; project_id:UUID|None=None; task_id:UUID|None=None; started_at:datetime|None=None; completed_at:datetime|None=None; estimated_cost:float|None=None; actual_cost:float|None=None; result:dict={}; error:str|None=None
