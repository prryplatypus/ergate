# Workflows

Workflows are a set of predefined steps that are aimed towards completing a specific task. They are identified by a constant, unique name.

Workflow steps are defined by using the `@workflow.step` decorator from the workflow object that you create. They are executed sequentially.


## Defining a workflow

Defining a workflow is extremely simple. All you have to do it import the class, create an object with a unique name and assign steps to it. Here's an example:

```py
from ergate import Workflow

workflow = Workflow(unique_name="my_first_workflow")

@workflow.step
def step_1() -> None:
    print("Hello, I am step 1")

@workflow.step
def step_2() -> None:
    print("Hello, I am step 2")
```


## Registering a workflow

Once you've defined a workflow, you need to let your Ergate application know that it exists. To do so, simply call the `register_workflow` method in your app instance with the workflow object you've created, like so:

```py
from ergate import Ergate
from .my_workflow import workflow

app = Ergate(..., ...)
app.register_workflow(workflow)
```
