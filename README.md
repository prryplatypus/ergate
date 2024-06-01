# Ergate
Workflows made easy, the agnostic way.

> [!NOTE]
> There's plenty of more features that aren't yet documented. For example, Ergate supports dependency injection via `Depends(...)` in a similar way to FastAPI. Feel free to open a GitHub issue if you have any questions while we work on adding documentation to the project.

## Simple example usage

```py
from ergate import Ergate, Job, Workflow

class WorkerQueue:
    def get_one(self) -> Job:
        ...  # You implement this

    def put(self, job: Job) -> None:
        ...  # You implement this

class JobStateStore:
    def update(self, job: Job) -> None:
        ...  # You implement this


workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def say_hi() -> None:
    print("Hello world")

@workflow.step
def say_bye() -> None:
    print("Goodbye world")

app = Ergate(queue=WorkerQueue(), job_state_store=JobStateStore())
app.register_workflow(workflow)

if __name__ == "__main__":
    app.run()
```


## Acknowledgements
- [Ziply Fiber](https://ziplyfiber.com): For giving me the initial idea to create this project and allowing me to turn it into a personal, open-source project.
- [FastAPI](https://github.com/tiangolo/fastapi): For inspiring me on the implementation of a bunch of the features supported by Ergate (such as the use of `Depends` for argument injection).
- [Sanic](https://github.com/sanic-org/sanic): For getting me originally into the open-source world and for their use of unique names in blueprints (similar to workflows in Ergate).
