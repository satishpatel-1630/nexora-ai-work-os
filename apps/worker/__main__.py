import asyncio
from apps.worker.runtime import WorkerRuntime
if __name__=="__main__": asyncio.run(WorkerRuntime().run())
