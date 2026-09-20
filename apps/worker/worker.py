import asyncio
import os

async def heartbeat() -> None:
    interval = float(os.getenv("NEXORA_WORKER_HEARTBEAT_SECONDS", "10"))
    while True:
        print("NEXORA worker heartbeat", flush=True)
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(heartbeat())
