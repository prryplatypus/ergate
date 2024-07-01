<style>
    .md-content .md-typeset h1 { display: none; }
</style>

# Ergate

<p align="center">
    <em>Ergate: workflows made easy, your way.</em>
</p>


## About

Ergate is a fully-typed framework upon which you can build distributed workers to process any given set of steps in a pre-defined order. Instead of restricting your choices to a given set of queues or state stores, Ergate simply defines a common set of functions that your queue and state store handlers must implement, leaving the implementation up to you.


## Installation

Ergate is available on PyPi, and therefore all you need to do to use it is `pip install` it:
```bash
pip install ergate
```


## Example

In this example, we're using a simple Python queue and triggering a Job manually just before running the app. However, the queue and state store implementations are completely up to you as long as they implement the methods shown here.

```py
from queue import Queue
from ergate import Ergate, Job, Workflow


queue: Queue[Job] = Queue()


class MyQueue:
    def get_one(self) -> Job:
        return queue.get()

    def put(self, job: Job) -> None:
        queue.put(job)


class MyStateStore:
    def update(self, job: Job) -> None:
        print(f"Updating {job.id}")


workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def say_hi() -> None:
    print("Hello world")


@workflow.step
def say_bye() -> None:
    print("Goodbye world")


app = Ergate(queue=MyQueue(), job_state_store=MyStateStore())
app.register_workflow(workflow)


if __name__ == "__main__":
    queue.put(Job(id=1, workflow_name="my_first_workflow"))
    app.run()
```


## Acknowledgements
- [Ziply Fiber](https://ziplyfiber.com){:target="_blank"}: For giving me the initial idea to create this project and allowing me to turn it into a personal, open-source project.
- [FastAPI](https://github.com/tiangolo/fastapi){:target="_blank"}: For inspiring me on the implementation of a bunch of the features supported by Ergate (such as the use of `Depends` for argument injection).
- [Sanic](https://github.com/sanic-org/sanic){:target="_blank"}: For getting me originally into the open-source world and for their use of unique names in blueprints (similar to workflows in Ergate).
