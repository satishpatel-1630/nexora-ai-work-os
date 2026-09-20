from apps.api.app.db.models import RiskLevel
from core.policy.engine import DefaultPolicyEngine
def test_public_requires_approval(): assert DefaultPolicyEngine().evaluate("publish",RiskLevel.EXTERNAL_PUBLIC).requires_approval
def test_read_only_does_not_require_approval(): assert not DefaultPolicyEngine().evaluate("inspect",RiskLevel.READ_ONLY).requires_approval
