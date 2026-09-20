import asyncio
from uuid import uuid4

from apps.api.app.contracts import Job
from apps.api.app.schemas import ApprovalCreate, ProjectUpdate, TaskUpdate
from apps.worker.runtime import RedisJobQueue


class FakeRedis:
    def __init__(self):
        self.items = []

    async def rpush(self, key, value):
        self.items.append((key, value))

    async def blpop(self, key, timeout=0):
        if not self.items:
            return None
        return self.items.pop(0)


def test_phase1_schemas_accept_expected_updates():
    assert ProjectUpdate(name="NEXORA", status="active").status == "active"
    assert TaskUpdate(title="ship", priority=2, status="in_progress").priority == 2
    approval = ApprovalCreate(
        action="deploy",
        target="production",
        reason="approved release",
        risk_level="external_public",
    )
    assert approval.risk_level == "external_public"


def test_redis_job_queue_round_trip():
    async def scenario():
        redis = FakeRedis()
        queue = RedisJobQueue(redis)
        job = Job(id=uuid4(), type="test", payload={"ok": True}, priority=3)
        await queue.enqueue(job)
        restored = await queue.dequeue()
        assert restored is not None
        assert restored.id == job.id
        assert restored.type == job.type
        assert restored.payload == job.payload
        assert restored.priority == 3

    asyncio.run(scenario())
