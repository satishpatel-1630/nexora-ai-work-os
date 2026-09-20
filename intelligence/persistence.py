from datetime import datetime,timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.models import IntelligenceRun,ResearchFindingRecord,TaskPlanRecord,SpecialistBriefRecord,PromptArtifactRecord,ModelInvocation,Event
from .models import IntelligenceResult
async def create_run(db:AsyncSession,request:str,project_id:UUID|None=None,task_id:UUID|None=None):
    row=IntelligenceRun(request=request,project_id=project_id,task_id=task_id,status="pending",current_stage="intent",result={}); db.add(row); db.add(Event(event_type="INTELLIGENCE_RUN_COMPLETED" if result.status.value=="completed" else "INTELLIGENCE_RUN_FAILED",project_id=row.project_id,task_id=row.task_id,payload={"run_id":str(row.id),"status":result.status.value}))\n    await db.commit(); await db.refresh(row); return row
async def get_run(db:AsyncSession,run_id:UUID): return (await db.execute(select(IntelligenceRun).where(IntelligenceRun.id==run_id))).scalar_one_or_none()
async def save_result(db:AsyncSession,row:IntelligenceRun,result:IntelligenceResult):
    row.status=result.status.value; row.current_stage=result.current_stage.value; row.started_at=row.started_at or datetime.now(timezone.utc); row.result=result.model_dump(mode="json"); row.error=result.error; row.completed_at=datetime.now(timezone.utc) if result.status.value in {"completed","failed"} else None
    if result.model_usage: row.estimated_cost=sum(x.estimated_cost or 0 for x in result.model_usage); row.actual_cost=sum(x.actual_cost or 0 for x in result.model_usage)
    for f in result.research: db.add(ResearchFindingRecord(intelligence_run_id=row.id,query=f.query,title=f.title,url=f.url,source=f.source,evidence=f.evidence,confidence=f.confidence,provider=f.provider,metadata_json=f.metadata))
    if result.plan: db.add(TaskPlanRecord(intelligence_run_id=row.id,plan=result.plan.model_dump(mode="json")))
    for b in result.briefs: db.add(SpecialistBriefRecord(intelligence_run_id=row.id,specialist=b.specialist,brief=b.model_dump(mode="json")))
    for i,p in enumerate(result.prompts): db.add(PromptArtifactRecord(intelligence_run_id=row.id,specialist=result.briefs[i].specialist if i<len(result.briefs) else None,prompt=p.model_dump(mode="json"),critique=result.critiques[i].model_dump(mode="json") if i<len(result.critiques) else {}))
    for u in result.model_usage: db.add(ModelInvocation(intelligence_run_id=row.id,provider=u.provider,model=u.model,input_tokens=u.input_tokens,output_tokens=u.output_tokens,latency_ms=u.latency_ms,estimated_cost=u.estimated_cost,actual_cost=u.actual_cost))
    await db.commit(); await db.refresh(row); return row
