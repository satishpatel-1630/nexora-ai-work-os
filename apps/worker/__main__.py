import asyncio

from apps.worker.runtime import WorkerRuntime


def main():
    asyncio.run(WorkerRuntime().run())


if __name__ == "__main__":
    main()
