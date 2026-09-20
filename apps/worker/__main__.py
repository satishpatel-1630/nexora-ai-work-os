import asyncio

from apps.worker.runtime import WorkerRuntime
from apps.worker.intelligence_handler import handle_intelligence_job


def main():
    asyncio.run(WorkerRuntime(handlers={"INTELLIGENCE_RUN": handle_intelligence_job}).run())


if __name__ == "__main__":
    main()
