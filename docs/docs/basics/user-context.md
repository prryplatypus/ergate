# User context

As you may have seen during the [jobs overview](./jobs-overview.md), the `Job` object has a `user_context` attribute that is marked as user-provided, but what is it used for exactly? Let's dig into it!

The idea behind `user_context` is to provide a way for you to store any arbitrary information that needs to be kept permanently and that isn't directly related to the execution of any of the steps (hence it not being useful as a return/input value).


## Passing user context

User context is a field in the `Job` model that can contain any kind of data. To use it, we simply have to create the `Job` object with the `user_context` parameter set to the desired value. How you get the data depends on your queue implementation.

Using the previous examples in the documentation, we're going to modify how we trigger the job we're queueing just before starting the app, so that its `user_context` contains information about the user who triggered the job.

```py title="app.py"
from ergate import Ergate, Job
from my_queue import MyQueue, queue
from my_state_store import MyStateStore
from my_workflow import workflow

app = Ergate(
    queue=MyQueue(),
    state_store=MyStateStore(),
)
app.register_workflow(workflow)

if __name__ == "__main__":
    job = Job(
        workflow_name="my_first_workflow",
        initial_input_value=21,
        user_context={"user": "prryplatypus"},
    )
    queue.put(job.model_dump(mode="json"))
    app.run()
```


## Accessing user context

Accessing user context is very similar to using dependencies, except instead of using `Depends(...)`, you must use `Context()` instead.

---

As always, it's challenge time! Can you modify the second step in our workflow so that it prints the name of the user that triggered the job? Give it a try and then check our solution below!

??? success "Solution"

    ```py title="my_workflow.py"
    from datetime import datetime
    from typing import Annotated, Any
    from ergate import Depends, Workflow, Context
    from my_dependency import create_current_time

    workflow = Workflow(unique_name="my_first_workflow")

    @workflow.step
    def step_1(
        input_value: int,
        now: Annotated[
            datetime,
            Depends(create_current_time),
        ],
    ) -> int:
        print(f"Hello, I am step 1 and I've received {input_value} at {now}")
        return input_value + 1

    @workflow.step
    def step_2(
        input_value: int,
        user_context: Annotated[
            dict[str, Any],
            Context(),
        ],
    ) -> None:
        print(
            f"Hello, I am step 2 and I've received {input_value} "
            f"thanks to {user_context['user']}"
        )
    ```
