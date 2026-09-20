from dataclasses import dataclass
from apps.api.app.db.models import RiskLevel
@dataclass(frozen=True)
class PolicyDecision:
    risk_level:RiskLevel; requires_approval:bool; reason:str
class DefaultPolicyEngine:
    def evaluate(self,action:str,risk_level:RiskLevel)->PolicyDecision:
        required=risk_level in {RiskLevel.LOCAL_DESTRUCTIVE,RiskLevel.EXTERNAL_PUBLIC,RiskLevel.HIGH_CONSEQUENCE}
        return PolicyDecision(risk_level,required,f"Policy evaluated action '{action}' at risk level '{risk_level.value}'.")
