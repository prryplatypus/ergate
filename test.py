from asyncio import Queue as AQueue

from ergate.app import Ergate
from ergate.job import Job
from ergate.workflow import Workflow


class Queue:
    def __init__(self) -> None:
        self.queue: AQueue[Job] = AQueue()

    async def put(self, job: Job) -> None:
        await self.queue.put(job)

    async def get_one(self) -> Job:
        return await self.queue.get()

    async def task_done(self) -> None:
        await self.queue.task_done()


class StateStore:
    async def save(self, job: Job) -> None:
        print(f"Saving job {job.id} to state store")


foo = Workflow("foo")


@foo.step
def step1():
    print("step1")
    return 1


@foo.step
def step2(inp: int, /):
    print(f"step2: {inp}")


ergate = Ergate(Queue(), StateStore())
ergate.register_workflow(foo)
ergate.run()
