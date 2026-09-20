from .pipeline import IntelligencePipeline
from .persistence import get_run,save_result
from apps.api.app.db.base import SessionLocal
from uuid import UUID
async def execute_run(run_id:UUID):
    async with SessionLocal() as db:
        row=await get_run(db,run_id)
        if row is None: return None
        row.status="running"; await db.commit()
        result=await IntelligencePipeline().run(row.request,run_id)
        return await save_result(db,row,result)
