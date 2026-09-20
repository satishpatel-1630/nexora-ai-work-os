from dataclasses import dataclass
from apps.api.app.config import get_settings
@dataclass(frozen=True)
class RoutingDecision:
    provider:str; model:str; reason:str; estimated_cost:float; estimated_latency_ms:int; fallbacks:list[str]
class CostRouter:
    def estimate(self,provider:str,model:str,input_chars:int,output_chars:int)->float:
        if provider=="mock": return 0.0
        return round((input_chars+output_chars)/1000000,6)
    def decide(self,provider:str,model:str,input_chars:int,output_chars:int)->RoutingDecision:
        cost=self.estimate(provider,model,input_chars,output_chars); budget=get_settings().ai_max_cost
        if cost>budget: raise ValueError("MODEL_BUDGET_EXCEEDED")
        return RoutingDecision(provider,model,"Configured provider within budget.",cost,1000,["mock"] if provider!="mock" else [])
class ModelRouter:
    def route(self,request:str)->RoutingDecision:
        s=get_settings(); return CostRouter().decide(s.ai_default_provider,s.gemini_model,len(request),4096)
