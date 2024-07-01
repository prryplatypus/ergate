# Input values

Being able to run workflows that don't depend on external data is cool and all, but most of the time you'll want to run workflows that use some variable input data. Ergate allows you to pass input values when running a workflow.


## Input values in the first step

The initial input value for a job is stored in the `initial_input_value` attribute of the `Job` model. This value is passed to the first step of the workflow when it is run if the step takes any input argument. Following the example from the previous section, let's modify the first step to take an input argument.

```py title="my_workflow.py"
from ergate import Workflow

workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def step_1(input_value: int) -> None:
    print(f"Hello, I am step 1 and I've received {input_value}")

@workflow.step
def step_2() -> None:
    print("Hello, I am step 2")
```

If we were processing a job with an initial input value of `21`, we would now see the following outputs:

- "Hello, I am step 1 and I've received 21"
- "Hello, I am step 2"


## Input values in subsequent steps

For any steps other than the first step, the input value they receive will be the return value from the previous step that got executed. This data is stored under the `last_return_value` attribute of the `Job` model. Let's modify the workflow so the second step receives some data from the first one.

```py title="my_workflow.py"
from ergate import Workflow

workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def step_1(input_value: int) -> int:
    print(f"Hello, I am step 1 and I've received {input_value}")
    return input_value + 1

@workflow.step
def step_2(input_value: int) -> None:
    print(f"Hello, I am step 2 and I've received {input_value}")
```

In this example, if we were processing a job with an initial input value of `21`, we would now see the following outputs:

- "Hello, I am step 1 and I've received 21"
- "Hello, I am step 2 and I've received 22"


## Passing an initial input value

Passing an initial input value to a job is simple. All you need to do is to provide the `initial_input_value` argument when creating the `Job` object.

---

Time for another small challenge. After replacing the demo workflow you have with the one above, can you modify the code from the previous section so that the job is triggered with an initial input value of `21`? Give it a try and then check our solution below!

??? success "Solution"

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
        job = Job(workflow_name="my_first_workflow", initial_input_value=21)
        queue.put(job.model_dump(mode="json"))
        app.run()
    ```
