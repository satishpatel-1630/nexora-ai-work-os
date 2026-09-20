import pytest
from intelligence.models import RunStatus
from intelligence.pipeline import IntelligencePipeline
from intelligence.registry import select_specialists
from intelligence.routing import ModelRouter

@pytest.mark.asyncio
async def test_mock_intelligence_pipeline_completes():
    result=await IntelligencePipeline().run("Create a 60-second Instagram Reel explaining EV adoption in India.")
    assert result.status==RunStatus.COMPLETED
    assert result.intent is not None
    assert result.plan is not None
    assert result.specialists is not None
    assert result.prompts
    assert result.model_usage[0].provider=="mock"

def test_specialist_selection_is_registry_backed():
    result=select_specialists("social",["script","instagram caption"],True)
    assert "research" in result.specialists
    assert "social_media" in result.specialists

def test_mock_cost_is_zero():
    decision=ModelRouter().route("test request")
    assert decision.estimated_cost==0
