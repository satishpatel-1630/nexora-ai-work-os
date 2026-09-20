from __future__ import annotations
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class RunStatus(StrEnum):
    PENDING="pending"; RUNNING="running"; COMPLETED="completed"; FAILED="failed"; CANCELLED="cancelled"
class Stage(StrEnum):
    INTENT="intent"; RESEARCH="research"; INTELLIGENCE="intelligence"; PLANNING="planning"; SPECIALISTS="specialists"; BRIEFS="briefs"; PROMPTING="prompting"; ROUTING="routing"; EXECUTION="execution"; COMPLETED="completed"

class IntentResult(BaseModel):
    intent:str; domain:str; urgency:str="normal"; requires_research:bool=False; requires_external_action:bool=False
    requested_deliverables:list[str]=Field(default_factory=list); audience:str|None=None; constraints:list[str]=Field(default_factory=list); confidence:float=Field(default=.8,ge=0,le=1)

class ResearchFinding(BaseModel):
    id:UUID=Field(default_factory=uuid4); query:str; title:str; url:str|None=None; source:str|None=None; evidence:str=""; published_at:datetime|None=None
    retrieved_at:datetime=Field(default_factory=lambda:datetime.now(UTC)); relevance:float=Field(default=.5,ge=0,le=1); confidence:float=Field(default=.5,ge=0,le=1)
    citations:list[dict[str,Any]]=Field(default_factory=list); provider:str="mock"; metadata:dict[str,Any]=Field(default_factory=dict)

class TaskIntelligenceResult(BaseModel):
    goal:str; context:str=""; requirements:list[str]=Field(default_factory=list); constraints:list[str]=Field(default_factory=list)
    audience:str|None=None; deliverables:list[str]=Field(default_factory=list); dependencies:list[str]=Field(default_factory=list); risks:list[str]=Field(default_factory=list)
    success_criteria:list[str]=Field(default_factory=list); research_findings:list[str]=Field(default_factory=list); recommended_specialists:list[str]=Field(default_factory=list)

class TaskStep(BaseModel):
    id:str; title:str; description:str; order:int; dependencies:list[str]=Field(default_factory=list); required_capabilities:list[str]=Field(default_factory=list)
    recommended_specialist:str|None=None; inputs:list[str]=Field(default_factory=list); expected_output:str=""; success_criteria:list[str]=Field(default_factory=list)
    estimated_cost:float=0; estimated_duration_seconds:int=0; risk_level:str="read_only"
class TaskPlan(BaseModel):
    steps:list[TaskStep]=Field(default_factory=list); rationale:str=""

class SpecialistProfile(BaseModel):
    name:str; description:str; capabilities:list[str]=Field(default_factory=list); domains:list[str]=Field(default_factory=list); input_types:list[str]=Field(default_factory=list)
    output_types:list[str]=Field(default_factory=list); model_requirements:list[str]=Field(default_factory=list); risk_profile:str="read_only"; available_tools:list[str]=Field(default_factory=list); quality_criteria:list[str]=Field(default_factory=list)
class SpecialistSelection(BaseModel):
    specialists:list[str]=Field(default_factory=list); rationale:str=""; required_capabilities:list[str]=Field(default_factory=list); confidence:float=Field(default=.8,ge=0,le=1)

class SpecialistBrief(BaseModel):
    specialist:str; objective:str; task_research:str=""; requirements:list[str]=Field(default_factory=list); constraints:list[str]=Field(default_factory=list); audience:str|None=None
    available_tools:list[str]=Field(default_factory=list); project_context:str|None=None; memory_context:str|None=None; brand_guidelines:str|None=None
    output_schema:dict[str,Any]=Field(default_factory=dict); quality_criteria:list[str]=Field(default_factory=list); failure_conditions:list[str]=Field(default_factory=list)

class PromptArtifact(BaseModel):
    version:int=1; system_instruction:str=""; developer_instruction:str=""; user_instruction:str=""; context:list[str]=Field(default_factory=list)
    output_schema:dict[str,Any]=Field(default_factory=dict); constraints:list[str]=Field(default_factory=list); quality_criteria:list[str]=Field(default_factory=list); model_parameters:dict[str,Any]=Field(default_factory=dict)

class PromptCritique(BaseModel):
    score:float=Field(default=.8,ge=0,le=1); issues:list[dict[str,Any]]=Field(default_factory=list); recommendations:list[str]=Field(default_factory=list); blocking_issues:list[str]=Field(default_factory=list)

class ModelRequest(BaseModel):
    model:str; system_instruction:str=""; input:str; structured_output_schema:dict[str,Any]|None=None; temperature:float=0.2; max_output_tokens:int=4096; timeout_seconds:float=60; tools:list[dict[str,Any]]=Field(default_factory=list); metadata:dict[str,Any]=Field(default_factory=dict)
class ModelUsage(BaseModel):
    provider:str; model:str; input_tokens:int=0; output_tokens:int=0; latency_ms:float|None=None; estimated_cost:float|None=None; actual_cost:float|None=None; quality_score:float|None=None
class ModelResponse(BaseModel):
    text:str=""; structured_output:dict[str,Any]|None=None; usage:ModelUsage; finish_reason:str|None=None; citations:list[dict[str,Any]]=Field(default_factory=list); metadata:dict[str,Any]=Field(default_factory=dict)

class IntelligenceResult(BaseModel):
    run_id:UUID; status:RunStatus; current_stage:Stage; intent:IntentResult|None=None; research:list[ResearchFinding]=Field(default_factory=list)
    task_intelligence:TaskIntelligenceResult|None=None; plan:TaskPlan|None=None; specialists:SpecialistSelection|None=None; briefs:list[SpecialistBrief]=Field(default_factory=list)
    prompts:list[PromptArtifact]=Field(default_factory=list); critiques:list[PromptCritique]=Field(default_factory=list); model_usage:list[ModelUsage]=Field(default_factory=list)
    final_output:dict[str,Any]=Field(default_factory=dict); error:str|None=None
