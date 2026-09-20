from __future__ import annotations
import json,time
from typing import Any,Protocol
from .models import ModelRequest,ModelResponse,ModelUsage,ResearchFinding
from apps.api.app.config import get_settings

class ModelProvider(Protocol):
    name:str
    async def complete(self,request:ModelRequest)->ModelResponse: ...
class ResearchProvider(Protocol):
    name:str
    async def research(self,query:str)->list[ResearchFinding]: ...

class MockProvider:
    name="mock"
    async def complete(self,request:ModelRequest)->ModelResponse:
        started=time.perf_counter(); schema=request.structured_output_schema or {}
        payload={}
        if schema.get("kind")=="intent": payload={"intent":"content_creation","domain":"social","urgency":"normal","requires_research":True,"requires_external_action":False,"requested_deliverables":["script","storyboard","social packaging"],"audience":"general social audience","constraints":["platform constraints"],"confidence":.9}
        elif schema.get("kind")=="task_intelligence": payload={"goal":request.input,"context":"Derived from the user request.","requirements":["fulfill the explicit request"],"constraints":[],"audience":"target audience","deliverables":["structured result"],"dependencies":[],"risks":[],"success_criteria":["meets requested deliverables"],"research_findings":[],"recommended_specialists":[]}
        elif schema.get("kind")=="plan": payload={"steps":[{"id":"step-1","title":"Research","description":"Gather relevant evidence.","order":1,"dependencies":[],"required_capabilities":["research"],"recommended_specialist":"research","inputs":[],"expected_output":"research findings","success_criteria":["sources recorded"],"estimated_cost":0,"estimated_duration_seconds":10,"risk_level":"read_only"}],"rationale":"Minimal deterministic plan for test execution."}
        else: payload={"result":"MockProvider completed the requested stage.","request":request.input}
        text=json.dumps(payload)
        return ModelResponse(text=text,structured_output=payload,usage=ModelUsage(provider=self.name,model=request.model,input_tokens=max(1,len(request.input)//4),output_tokens=max(1,len(text)//4),latency_ms=(time.perf_counter()-started)*1000,estimated_cost=0,actual_cost=0),finish_reason="stop")

class MockResearchProvider:
    name="mock"
    async def research(self,query:str)->list[ResearchFinding]:
        return [ResearchFinding(query=query,title="Mock research result",url=None,source="mock",evidence=f"Deterministic research placeholder for: {query}",relevance=1,confidence=.5)]

class GeminiProvider:
    name="gemini"
    def __init__(self):
        from google import genai
        self.client=genai.Client(api_key=get_settings().gemini_api_key)
        self.model=get_settings().gemini_model
    async def complete(self,request:ModelRequest)->ModelResponse:
        import asyncio
        started=time.perf_counter()
        from google.genai import types
        config=types.GenerateContentConfig(system_instruction=request.system_instruction or None,temperature=request.temperature,max_output_tokens=request.max_output_tokens)
        if request.structured_output_schema:
            config.response_mime_type="application/json"
            config.response_schema=request.structured_output_schema
        response=await asyncio.to_thread(self.client.models.generate_content,model=request.model or self.model,contents=request.input,config=config)
        text=getattr(response,"text","") or ""
        structured=None
        if request.structured_output_schema:
            try: structured=json.loads(text)
            except json.JSONDecodeError: structured=None
        usage_meta=getattr(response,"usage_metadata",None)
        input_tokens=getattr(usage_meta,"prompt_token_count",0) or 0
        output_tokens=getattr(usage_meta,"candidates_token_count",0) or 0
        return ModelResponse(text=text,structured_output=structured,usage=ModelUsage(provider=self.name,model=request.model or self.model,input_tokens=input_tokens,output_tokens=output_tokens,latency_ms=(time.perf_counter()-started)*1000),metadata={"raw_type":type(response).__name__})

class GeminiResearchProvider(GeminiProvider):
    async def research(self,query:str)->list[ResearchFinding]:
        import asyncio
        from google.genai import types
        response=await asyncio.to_thread(self.client.models.generate_content,model=self.model,contents=query,config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]))
        findings=[]; candidate=(getattr(response,"candidates",None) or [None])[0]; metadata=getattr(candidate,"grounding_metadata",None) if candidate else None
        chunks=getattr(metadata,"grounding_chunks",[]) if metadata else []
        for chunk in chunks:
            web=getattr(chunk,"web",None)
            if web: findings.append(ResearchFinding(query=query,title=getattr(web,"title","") or "Web source",url=getattr(web,"uri",None),source=getattr(web,"title",None),evidence=getattr(response,"text","")[:1000],confidence=.8,provider=self.name,citations=[{"title":getattr(web,"title","") or "Web source","url":getattr(web,"uri",None)}]))
        return findings or [ResearchFinding(query=query,title="Gemini grounded response",evidence=getattr(response,"text","")[:4000],confidence=.7,provider=self.name)]
