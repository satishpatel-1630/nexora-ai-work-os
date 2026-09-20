from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.models import (
    Event,
    IntelligenceRun,
    ModelInvocation,
    PromptArtifactRecord,
    ResearchFindingRecord,
    SpecialistBriefRecord,
    TaskPlanRecord,
)
from .models import IntelligenceResult


async def create_run(db: AsyncSession, request: str, project_id: UUID | None = None, task_id: UUID | None = None):
    row = IntelligenceRun(
        request=request,
        project_id=project_id,
        task_id=task_id,
        status="pending",
        current_stage="intent",
        result={},
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_run(db: AsyncSession, run_id: UUID):
    result = await db.execute(select(IntelligenceRun).where(IntelligenceRun.id == run_id))
    return result.scalar_one_or_none()


async def save_result(db: AsyncSession, row: IntelligenceRun, result: IntelligenceResult):
    row.status = result.status.value
    row.current_stage = result.current_stage.value
    row.started_at = row.started_at or datetime.now(UTC)
    row.result = result.model_dump(mode="json")
    row.error = result.error
    if result.status.value in {"completed", "failed"}:
        row.completed_at = datetime.now(UTC)
    if result.model_usage:
        row.estimated_cost = sum(x.estimated_cost or 0 for x in result.model_usage)
        row.actual_cost = sum(x.actual_cost or 0 for x in result.model_usage)

    for finding in result.research:
        db.add(
            ResearchFindingRecord(
                intelligence_run_id=row.id,
                query=finding.query,
                title=finding.title,
                url=finding.url,
                source=finding.source,
                evidence=finding.evidence,
                confidence=finding.confidence,
                provider=finding.provider,
                metadata_json=finding.metadata,
            )
        )
    if result.plan:
        db.add(TaskPlanRecord(intelligence_run_id=row.id, plan=result.plan.model_dump(mode="json")))
    for brief in result.briefs:
        db.add(
            SpecialistBriefRecord(
                intelligence_run_id=row.id,
                specialist=brief.specialist,
                brief=brief.model_dump(mode="json"),
            )
        )
    for index, prompt in enumerate(result.prompts):
        db.add(
            PromptArtifactRecord(
                intelligence_run_id=row.id,
                specialist=result.briefs[index].specialist if index < len(result.briefs) else None,
                prompt=prompt.model_dump(mode="json"),
                critique=result.critiques[index].model_dump(mode="json") if index < len(result.critiques) else {},
            )
        )
    for usage in result.model_usage:
        db.add(
            ModelInvocation(
                intelligence_run_id=row.id,
                provider=usage.provider,
                model=usage.model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                latency_ms=usage.latency_ms,
                estimated_cost=usage.estimated_cost,
                actual_cost=usage.actual_cost,
            )
        )

    db.add(
        Event(
            event_type="INTELLIGENCE_RUN_COMPLETED"
            if result.status.value == "completed"
            else "INTELLIGENCE_RUN_FAILED",
            project_id=row.project_id,
            task_id=row.task_id,
            payload={"run_id": str(row.id), "status": result.status.value},
        )
    )
    await db.commit()
    await db.refresh(row)
    return row
