# Using workflow step names for manual ordering

Workflow steps may be manually ordered and redirected by use of `GoToEnd`, `GoToStep` and `SkipNSteps` exceptions.

Workflow ordering can be preempted and redirected by raising the `GoToStep` exception, passing the workflow step 
function along with the optional return value.

Workflows may also be advanced directly to completion by raising the `GoToEnd` exception.

Workflows may also be advanced by a set number of steps by raising the `SkipNSteps` exception.

## Defining manual workflow order

The following workflow contains five steps in total, which are executed in a specific order as directed by the 
exceptions.

```py title="my_ordered_workflow.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="my_ordered_workflow")

@workflow.step
def step_1() -> None:
    print("Hello, I am step 1")

@workflow.step
def step_2() -> None:
    print("Hello, I am step 2")
    raise GoToStep(step_4)

@workflow.step
def step_3() -> None:
    print("Hello, I am step 3")

@workflow.step
def step_4() -> None:
    print("Hello, I am step 4")
    raise GoToStep(step_5)

@workflow.step
def step_5() -> None:
    print("Hello, I am step 5")
    raise GoToEnd()
```

`step_1` and `step_2` execute in normal sequence order.  However, `step_2` raises the `GoToStep` exception for `step_4`,
which alters the execution order.  `step_3` is skipped, and the workflow proceeds directly to `step_4`.  `step_4` also 
raises `GoToStep` for `step_5`, altering the order and proceeding to that function.  Finally, `step_5` executes, and 
then raises `GoToEnd` to complete the workflow.

The resulting order is:

1. `step_1`
2. `step_2`
3. `step_4`
4. `step_5`

Without the `GoToStep` exception being utilised, this workflow would execute in the source ordering:

1. `step_1`
2. `step_2`
4. `step_3`
5. `step_4`
3. `step_5`

This trivial example may seem pointless, as one could readily omit `step_3` and negate the need for manual ordering 
with these exceptions.  However, these features allow for branching of workflows according to arbitrary conditions.

Consider the following bifurcated workflow.

```py title="my_ordered_workflow_2.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="my_ordered_workflow_2")

@workflow.step
def step_1(input_value: str) -> None:
    print("Hello, I am step 1")
    
    match input_value:
        case "a":
            raise GoToStep(step_a2)
        case "b":
            raise GoToStep(step_b2)
        case "c":
            raise GoToStep(step_c2)
        case _:
            raise GoToStep(step_default2)

@workflow.step
def step_default2() -> None:
    print("Hello, I am step default.2")
    raise GoToStep(step_4)

@workflow.step
def step_a2() -> None:
    print("Hello, I am step a.2")

@workflow.step
def step_a3() -> None:
    print("Hello, I am step a.3")
    raise GoToStep(step_4)

@workflow.step
def step_b2() -> None:
    print("Hello, I am step b.2")

@workflow.step
def step_b3() -> None:
    print("Hello, I am step b.3")
    raise GoToStep(step_4)

@workflow.step
def step_c2() -> None:
    print("Hello, I am step c.2")

@workflow.step
def step_c3() -> None:
    print("Hello, I am step c.3")
    # Skip remaining steps and complete workflow immediately.
    raise GoToEnd()

@workflow.step
def step_4() -> None:
    print("Hello, I am step 4")
```

In this case, there are four possible paths for the workflow to take, based on the value of `input_value`:

If `input_value` is `a`, the workflow path is:

1. `step_1`
2. `step_a2`
3. `step_a3`
4. `step_4`

If `input_value` is `b`, the workflow path is:

1. `step_1`
2. `step_b2`
3. `step_b3`
4. `step_4`

If `input_value` is `c`, the workflow path is:

1. `step_1`
2. `step_c2`
3. `step_c3`

with `step_4` skipped by the `GoToEnd` raised in `step_c3`.

If `input_value` is anything else, the workflow path is:

1. `step_1`
2. `step_default2`
4. `step_4`

Note that the length of the workflows can vary when utilising these exceptions.

## Errata
* Because of how the `percent_completed` and `total_steps` values are calculated, utilising manual step ordering with 
the related exceptions can cause the percentage and total step calculations to be inaccurate.  It is recommended when 
utilising this feature to define the `paths` each step may follow in the `step()` decorator, to allow Ergate to better 
calculate and predict values for `percent_completed` and `total_steps`.  Although they will still not always be fully 
accurate, they will be progressive (never reducing back to a lower count of steps completed) and grow in accuracy as 
the workflow progresses. 

* _Nota bene_: it is currently not permitted to use `GoToStep` to go to a previous step in the workflow.  There is no 
technical reason behind this limitation, and it may be added in a future release.