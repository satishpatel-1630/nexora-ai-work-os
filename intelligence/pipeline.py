from uuid import UUID, uuid4

from apps.api.app.config import get_settings

from .models import (
    IntelligenceResult,
    IntentResult,
    ModelRequest,
    PromptArtifact,
    PromptCritique,
    RunStatus,
    SpecialistBrief,
    Stage,
    TaskIntelligenceResult,
    TaskPlan,
)
from .providers import GeminiProvider, GeminiResearchProvider, MockProvider, MockResearchProvider
from .registry import select_specialists
from .routing import ModelRouter


class IntelligencePipeline:
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        if settings.ai_default_provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is required when AI_DEFAULT_PROVIDER=gemini")
            self.provider = GeminiProvider()
            self.research_provider = GeminiResearchProvider()
        else:
            self.provider = MockProvider()
            self.research_provider = MockResearchProvider()

    async def run(self, request: str, run_id: UUID | None = None) -> IntelligenceResult:
        result = IntelligenceResult(
            run_id=run_id or uuid4(),
            status=RunStatus.RUNNING,
            current_stage=Stage.INTENT,
        )
        try:
            intent_response = await self.provider.complete(
                ModelRequest(
                    model=self.settings.gemini_model,
                    input=request,
                    structured_output_schema={"kind": "intent"},
                    max_output_tokens=1000,
                )
            )
            result.intent = IntentResult.model_validate(intent_response.structured_output or {})
            result.current_stage = Stage.RESEARCH

            if result.intent.requires_research and self.settings.ai_research_enabled:
                result.research = await self.research_provider.research(request)

            result.current_stage = Stage.INTELLIGENCE
            intelligence_response = await self.provider.complete(
                ModelRequest(
                    model=self.settings.gemini_model,
                    input=request,
                    structured_output_schema={"kind": "task_intelligence"},
                    max_output_tokens=1600,
                )
            )
            result.task_intelligence = TaskIntelligenceResult.model_validate(
                intelligence_response.structured_output or {}
            )
            result.task_intelligence.research_findings = [finding.evidence for finding in result.research]

            result.current_stage = Stage.PLANNING
            plan_response = await self.provider.complete(
                ModelRequest(
                    model=self.settings.gemini_model,
                    input=request,
                    structured_output_schema={"kind": "plan"},
                    max_output_tokens=1800,
                )
            )
            result.plan = TaskPlan.model_validate(plan_response.structured_output or {})

            result.current_stage = Stage.SPECIALISTS
            result.specialists = select_specialists(
                result.intent.domain,
                result.intent.requested_deliverables,
                result.intent.requires_research,
            )

            if result.intent.requires_research and self.settings.ai_research_enabled:
                specialist_findings = []
                for specialist in result.specialists.specialists:
                    specialist_findings.extend(
                        await self.research_provider.research(
                            f"{request} requirements for {specialist} specialist"
                        )
                    )
                result.research.extend(specialist_findings)

            result.current_stage = Stage.BRIEFS
            for specialist in result.specialists.specialists:
                result.briefs.append(
                    SpecialistBrief(
                        specialist=specialist,
                        objective=result.task_intelligence.goal,
                        task_research="\n".join(finding.evidence for finding in result.research),
                        requirements=result.task_intelligence.requirements,
                        constraints=result.task_intelligence.constraints,
                        audience=result.intent.audience,
                        output_schema={"type": "object"},
                        quality_criteria=["fulfill requirements"],
                        failure_conditions=["missing required deliverables"],
                    )
                )

            result.current_stage = Stage.PROMPTING
            for brief in result.briefs:
                result.prompts.append(
                    PromptArtifact(
                        system_instruction=f"You are the {brief.specialist} specialist.",
                        user_instruction=brief.objective,
                        context=[brief.task_research],
                        output_schema=brief.output_schema,
                        constraints=brief.constraints,
                        quality_criteria=brief.quality_criteria,
                    )
                )
                result.critiques.append(
                    PromptCritique(
                        score=0.9,
                        recommendations=["Keep requirements explicit."],
                    )
                )

            result.current_stage = Stage.ROUTING
            decision = ModelRouter().route(request)

            result.current_stage = Stage.EXECUTION
            final_response = await self.provider.complete(
                ModelRequest(
                    model=decision.model,
                    system_instruction="Return a concise structured result.",
                    input=request,
                    structured_output_schema={"kind": "final"},
                )
            )
            result.model_usage.append(final_response.usage)
            result.final_output = final_response.structured_output or {"text": final_response.text}
            result.current_stage = Stage.COMPLETED
            result.status = RunStatus.COMPLETED
            return result
        except Exception as exc:
            result.status = RunStatus.FAILED
            result.error = str(exc)
            return result
