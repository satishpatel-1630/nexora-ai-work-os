from uuid import UUID
from .pipeline import IntelligencePipeline

class IntelligenceService:
    def __init__(self,pipeline=None): self.pipeline=pipeline or IntelligencePipeline()
    async def execute(self,request:str,run_id:UUID|None=None): return await self.pipeline.run(request,run_id)
