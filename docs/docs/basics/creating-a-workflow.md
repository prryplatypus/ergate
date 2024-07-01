# Creating a workflow

Workflows are a set of predefined steps that are aimed towards completing a specific task. They are identified by a constant, unique name.

Workflow steps are created by using the `step` decorator on a workflow object. Steps are executed sequentially.


## Defining a workflow

Defining a workflow is extremely simple. All you have to do it import the class, create an object with a unique name and assign steps to it. Here's an example:

```py title="my_workflow.py"
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

Once you've defined a workflow, you need to let your Ergate application know that it exists. To do so, simply call the `register_workflow` method in your app instance with the workflow object you've created.

!!! info

    Running this will make the app appear "stuck". The reason for this is that there's no jobs in the queue. We'll cover that in the next section.

```py title="app.py"
from ergate import Ergate
from my_queue import MyQueue
from my_state_store import MyStateStore
from my_workflow import workflow

app = Ergate(
    queue=MyQueue(),
    state_store=MyStateStore(),
)
app.register_workflow(workflow)

if __name__ == "__main__":
    app.run()
```
