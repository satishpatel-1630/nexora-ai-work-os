from datetime import datetime
from enum import StrEnum
from uuid import UUID,uuid4
from sqlalchemy import DateTime,ForeignKey,Integer,String,Text,func
from sqlalchemy.dialects.postgresql import JSONB,UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
class Base(DeclarativeBase): pass
class ProjectStatus(StrEnum): ACTIVE="active"; PAUSED="paused"; COMPLETED="completed"; ARCHIVED="archived"
class TaskStatus(StrEnum): TODO="todo"; IN_PROGRESS="in_progress"; COMPLETED="completed"; FAILED="failed"; CANCELLED="cancelled"
class ApprovalStatus(StrEnum): PENDING="pending"; APPROVED="approved"; REJECTED="rejected"; EXPIRED="expired"; CANCELLED="cancelled"
class RiskLevel(StrEnum): READ_ONLY="read_only"; LOCAL_REVERSIBLE="local_reversible"; LOCAL_DESTRUCTIVE="local_destructive"; EXTERNAL_REVERSIBLE="external_reversible"; EXTERNAL_PUBLIC="external_public"; HIGH_CONSEQUENCE="high_consequence"
class Project(Base):
    __tablename__="projects"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4)
    name:Mapped[str]=mapped_column(String(200)); description:Mapped[str|None]=mapped_column(Text,nullable=True)
    status:Mapped[ProjectStatus]=mapped_column(String(32),default=ProjectStatus.ACTIVE); metadata_json:Mapped[dict]=mapped_column("metadata",JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    tasks:Mapped[list["Task"]]=relationship(back_populates="project",cascade="all, delete-orphan")
class Task(Base):
    __tablename__="tasks"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); project_id:Mapped[UUID]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE"),index=True)
    title:Mapped[str]=mapped_column(String(240)); description:Mapped[str|None]=mapped_column(Text,nullable=True); status:Mapped[TaskStatus]=mapped_column(String(32),default=TaskStatus.TODO)
    priority:Mapped[int]=mapped_column(Integer,default=0); metadata_json:Mapped[dict]=mapped_column("metadata",JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    project:Mapped[Project]=relationship(back_populates="tasks")
class Event(Base):
    __tablename__="events"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); event_type:Mapped[str]=mapped_column(String(100),index=True)
    project_id:Mapped[UUID|None]=mapped_column(ForeignKey("projects.id",ondelete="SET NULL"),nullable=True,index=True); task_id:Mapped[UUID|None]=mapped_column(ForeignKey("tasks.id",ondelete="SET NULL"),nullable=True,index=True)
    payload:Mapped[dict]=mapped_column(JSONB,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class ApprovalRequest(Base):
    __tablename__="approval_requests"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); action:Mapped[str]=mapped_column(String(240)); target:Mapped[str]=mapped_column(String(500)); reason:Mapped[str]=mapped_column(Text)
    risk_level:Mapped[RiskLevel]=mapped_column(String(40)); status:Mapped[ApprovalStatus]=mapped_column(String(32),default=ApprovalStatus.PENDING,index=True)
    proposed_changes:Mapped[dict]=mapped_column(JSONB,default=dict); estimated_cost:Mapped[float|None]=mapped_column(nullable=True); preview:Mapped[dict]=mapped_column(JSONB,default=dict); metadata_json:Mapped[dict]=mapped_column("metadata",JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); resolved_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)

class IntelligenceRun(Base):
    __tablename__="intelligence_runs"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4)
    project_id:Mapped[UUID|None]=mapped_column(ForeignKey("projects.id",ondelete="SET NULL"),nullable=True,index=True)
    task_id:Mapped[UUID|None]=mapped_column(ForeignKey("tasks.id",ondelete="SET NULL"),nullable=True,index=True)
    request:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(32),default="pending",index=True)
    current_stage:Mapped[str]=mapped_column(String(40),default="intent"); started_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True); estimated_cost:Mapped[float|None]=mapped_column(nullable=True); actual_cost:Mapped[float|None]=mapped_column(nullable=True)
    result:Mapped[dict]=mapped_column(JSONB,default=dict); error:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class ResearchFindingRecord(Base):
    __tablename__="research_findings"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); intelligence_run_id:Mapped[UUID]=mapped_column(ForeignKey("intelligence_runs.id",ondelete="CASCADE"),index=True)
    query:Mapped[str]=mapped_column(Text); title:Mapped[str]=mapped_column(String(500)); url:Mapped[str|None]=mapped_column(Text,nullable=True); source:Mapped[str|None]=mapped_column(String(300),nullable=True)
    evidence:Mapped[str]=mapped_column(Text); confidence:Mapped[float]=mapped_column(default=.5); provider:Mapped[str]=mapped_column(String(80)); metadata_json:Mapped[dict]=mapped_column("metadata",JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class TaskPlanRecord(Base):
    __tablename__="task_plans"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); intelligence_run_id:Mapped[UUID]=mapped_column(ForeignKey("intelligence_runs.id",ondelete="CASCADE"),unique=True,index=True); plan:Mapped[dict]=mapped_column(JSONB,default=dict)
class SpecialistBriefRecord(Base):
    __tablename__="specialist_briefs"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); intelligence_run_id:Mapped[UUID]=mapped_column(ForeignKey("intelligence_runs.id",ondelete="CASCADE"),index=True); specialist:Mapped[str]=mapped_column(String(120)); brief:Mapped[dict]=mapped_column(JSONB,default=dict)
class PromptArtifactRecord(Base):
    __tablename__="prompt_artifacts"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); intelligence_run_id:Mapped[UUID]=mapped_column(ForeignKey("intelligence_runs.id",ondelete="CASCADE"),index=True); specialist:Mapped[str|None]=mapped_column(String(120),nullable=True); prompt:Mapped[dict]=mapped_column(JSONB,default=dict); critique:Mapped[dict]=mapped_column(JSONB,default=dict)
class ModelInvocation(Base):
    __tablename__="model_invocations"
    id:Mapped[UUID]=mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid4); intelligence_run_id:Mapped[UUID]=mapped_column(ForeignKey("intelligence_runs.id",ondelete="CASCADE"),index=True)
    provider:Mapped[str]=mapped_column(String(80)); model:Mapped[str]=mapped_column(String(160)); input_tokens:Mapped[int]=mapped_column(Integer,default=0); output_tokens:Mapped[int]=mapped_column(Integer,default=0)
    latency_ms:Mapped[float|None]=mapped_column(nullable=True); estimated_cost:Mapped[float|None]=mapped_column(nullable=True); actual_cost:Mapped[float|None]=mapped_column(nullable=True); metadata_json:Mapped[dict]=mapped_column("metadata",JSONB,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
