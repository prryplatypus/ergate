# Flow control

Normally, **Ergate** runs the workflow steps for you in order, one by one and one after the other. However, in some cases you might want some manual control over this, and you may want to skip some steps or stop running the job altogether. **Ergate** allows you to do this through the use of exceptions.


## Skipping steps

In order to skip an arbitrary number of steps, **Ergate** provides a `SkipNSteps` exception. This exception takes two arguments:

- `n`: The number of steps to skip. If n is greater than the number of steps left to run, the job will be marked as completed.
- `retval`: Since it's not possible to return a value from a step after having raised an exception, you can pass an input value for the next step to be run by using this argument.

Let's add another step to the workflow from previous sections and raise this exception from the first step so that the second step is skipped. We'll also remove all of the context and dependency-related code to keep things simple.

```py title="my_workflow.py"
from datetime import datetime
from typing import Annotated, Any
from ergate import SkipNSteps, Workflow
from my_dependency import create_current_time

workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def step_1(input_value: int) -> int:
    print(f"Hello, I am step 1 and I've received {input_value}")
    raise SkipNSteps(n=1, retval=input_value + 1)

@workflow.step
def step_2(input_value: int) -> None: #(1)!
    print(f"Hello, I am step 2 and I've received {input_value}")

@workflow.step
def step_3(input_value: int) -> None:
    print(f"Hello, I am step 3 and I've received {input_value}")
```

1. This step will be skipped.

In this example, if we were processing a job with an initial input value of `21`, we would now see the following outputs:

- "Hello, I am step 1 and I've received 21"
- "Hello, I am step 3 and I've received 22"


## Aborting the job

As you may have seen during the [jobs overview](./jobs-overview.md), the `JobStatus` enum has an `ABORTED` status. In **Ergate**, `ABORTED` means "intentionally failed/not completed".

To abort a job, you can raise the `AbortJob` exception. This exception takes one argument:

- `message`: A message to explain why the job was aborted.

---

It's challenge time! Modify the first step in our workflow so that -before doing anything else- it aborts the job if the input value is less than 20. Give it a try and then check our solution below!

??? success "Solution"

    ```py title="my_workflow.py"
    from datetime import datetime
    from typing import Annotated, Any
    from ergate import AbortJob, Workflow
    from my_dependency import create_current_time

    workflow = Workflow(unique_name="my_first_workflow")

    @workflow.step
    def step_1(input_value: int) -> int:
        if input_value < 20:
            raise AbortJob("Input value is less than 20")
        print(f"Hello, I am step 1 and I've received {input_value}")
        raise SkipNSteps(n=1, retval=input_value + 1)

    @workflow.step
    def step_2(input_value: int) -> None:
        print(f"Hello, I am step 2 and I've received {input_value}")

    @workflow.step
    def step_3(input_value: int) -> None:
        print(f"Hello, I am step 3 and I've received {input_value}")
    ```
