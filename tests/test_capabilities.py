from capabilities.registry import CapabilityRegistry
def test_core_capabilities(): assert CapabilityRegistry().get("TEXT_GENERATION") and CapabilityRegistry().get("VIDEO_EDITING")
