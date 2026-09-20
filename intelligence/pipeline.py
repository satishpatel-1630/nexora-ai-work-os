from __future__ import annotations
from uuid import UUID,uuid4
from .models import *
from .providers import MockProvider,MockResearchProvider,GeminiProvider,GeminiResearchProvider
from .registry import select_specialists
from apps.api.app.config import get_settings

class IntelligencePipeline:
    def __init__(self):
        s=get_settings(); self.settings=s
        self.provider=MockProvider() if s.ai_default_provider=="mock" else GeminiProvider()
        self.research_provider=MockResearchProvider() if s.ai_default_provider=="mock" else GeminiResearchProvider()
    async def run(self,request:str,run_id:UUID|None=None)->IntelligenceResult:
        rid=run_id or uuid4(); result=IntelligenceResult(run_id=rid,status=RunStatus.RUNNING,current_stage=Stage.INTENT)
        try:
            intent=await self.provider.complete(ModelRequest(model=self.settings.gemini_model,input=request,structured_output_schema={"kind":"intent"},max_output_tokens=1000))
            result.intent=IntentResult.model_validate(intent.structured_output or {})
            result.current_stage=Stage.RESEARCH
            if result.intent.requires_research:
                result.research=await self.research_provider.research(request)
            result.current_stage=Stage.INTELLIGENCE
            ti=await self.provider.complete(ModelRequest(model=self.settings.gemini_model,input=request,structured_output_schema={"kind":"task_intelligence"},max_output_tokens=1600))
            result.task_intelligence=TaskIntelligenceResult.model_validate(ti.structured_output or {})
            result.task_intelligence.research_findings=[x.evidence for x in result.research]
            result.current_stage=Stage.PLANNING
            plan=await self.provider.complete(ModelRequest(model=self.settings.gemini_model,input=request,structured_output_schema={"kind":"plan"},max_output_tokens=1800))
            result.plan=TaskPlan.model_validate(plan.structured_output or {})
            result.current_stage=Stage.SPECIALISTS
            result.specialists=select_specialists(result.intent.domain,result.intent.requested_deliverables,result.intent.requires_research)
            result.current_stage=Stage.BRIEFS
            for name in result.specialists.specialists:
                result.briefs.append(SpecialistBrief(specialist=name,objective=result.task_intelligence.goal,task_research="\n".join(x.evidence for x in result.research),requirements=result.task_intelligence.requirements,constraints=result.task_intelligence.constraints,audience=result.intent.audience,output_schema={"type":"object"},quality_criteria=["fulfill requirements"],failure_conditions=["missing required deliverables"]))
            result.current_stage=Stage.PROMPTING
            for brief in result.briefs:
                prompt=PromptArtifact(system_instruction=f"You are the {brief.specialist} specialist.",user_instruction=brief.objective,context=[brief.task_research],output_schema=brief.output_schema,constraints=brief.constraints,quality_criteria=brief.quality_criteria)
                result.prompts.append(prompt); result.critiques.append(PromptCritique(score=.9,recommendations=["Keep requirements explicit."],issues=[]))
            result.current_stage=Stage.ROUTING
            result.current_stage=Stage.EXECUTION
            final=await self.provider.complete(ModelRequest(model=self.settings.gemini_model,system_instruction="Return a concise structured result.",input=request,structured_output_schema={"kind":"final"}))
            result.model_usage.append(final.usage); result.final_output=final.structured_output or {"text":final.text}
            result.current_stage=Stage.COMPLETED; result.status=RunStatus.COMPLETED
            return result
        except Exception as exc:
            result.status=RunStatus.FAILED; result.error=str(exc); return result
