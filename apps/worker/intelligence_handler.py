from apps.api.app.contracts import Job
from intelligence.orchestration import execute_run
from uuid import UUID

async def handle_intelligence_job(job: Job) -> None:
    run_id = job.payload.get("run_id")
    if run_id:
        await execute_run(UUID(run_id))
