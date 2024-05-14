from multiprocessing import Queue as MQueue
from time import sleep

from ergate.app import Ergate
from ergate.job import Job
from ergate.workflow import Workflow


class Queue:
    def __init__(self) -> None:
        self.queue: MQueue[Job] = MQueue()

    def put(self, job: Job) -> None:
        self.queue.put(job)

    def get_one(self) -> Job:
        return self.queue.get()

    def task_done(self) -> None:
        pass


class StateStore:
    def save(self, job: Job) -> None:
        print(f"Saving job {job.id} to state store")


foo = Workflow("foo")


@foo.step
def step1():
    print("step1")
    sleep(10)
    print("step1 done")
    return 1


@foo.step
def step2(inp: int, /):
    print(f"step2: {inp}")


queue = Queue()
queue.put(Job(workflow_name="foo", id="1"))


ergate = Ergate(queue, StateStore())
ergate.register_workflow(foo)
ergate.run()
