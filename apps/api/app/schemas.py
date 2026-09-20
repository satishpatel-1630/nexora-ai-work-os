from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from apps.api.app.db.models import ApprovalStatus, ProjectStatus, RiskLevel, TaskStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: ProjectStatus | None = None
    metadata: dict | None = None


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True, validate_by_alias=True)
    id: UUID
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(validation_alias=AliasChoices("metadata", "metadata_json"))


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    description: str | None = None
    priority: int = Field(default=0, ge=0)
    metadata: dict = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = None
    priority: int | None = Field(default=None, ge=0)
    status: TaskStatus | None = None
    metadata: dict | None = None


class TaskRead(TaskCreate):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True, validate_by_alias=True)
    id: UUID
    project_id: UUID
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(validation_alias=AliasChoices("metadata", "metadata_json"))


class ApprovalCreate(BaseModel):
    action: str = Field(min_length=1, max_length=240)
    target: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=1)
    risk_level: RiskLevel
    proposed_changes: dict = Field(default_factory=dict)
    estimated_cost: float | None = Field(default=None, ge=0)
    preview: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True, validate_by_alias=True)
    id: UUID
    action: str
    target: str
    reason: str
    risk_level: RiskLevel
    status: ApprovalStatus
    proposed_changes: dict
    estimated_cost: float | None
    preview: dict
    metadata: dict = Field(validation_alias=AliasChoices("metadata", "metadata_json"))
    created_at: datetime
    resolved_at: datetime | None
