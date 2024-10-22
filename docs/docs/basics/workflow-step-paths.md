# Defining workflow paths

In order to facilitate labelled workflow steps with branching paths, speculative logic was included to predict the total
number of steps for the workflow and thereby calculate the completion percentage.

These may be seen as similar to Python type hints, in that they do not directly affect the flow and operation of the 
workflow, but provide metadata allowing the engine to better determine information about the workflow operaion, viz. the
completion percentage and total steps.

This logic may be enabled by specifying the `paths=` kwarg for a given `@workflow.step()` decorator.

* It is not necessary to specify `paths` for workflow steps which only return a value via `return`, thus maintaining full compatibility with existing code.
* It is suggested to define `paths` for steps which utilise the `SkipNSteps` or `GoToEnd` exceptions. 
* It is recommended to define `paths` for steps which utilise the `GoToStep` exception, or which have branching logic with multiple potential paths.

`paths` may be freely defined alongside other kwargs in the `@workflow.step` decorator.

## Defining workflow paths
When defining `paths`, each potential path should be specified by its Exception.


```py title="workflow_with_paths.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="my_third_workflow")

@workflow.step
def step_1() -> int:
    print("Hello, I am step 1")
    return 1

@workflow.step(paths=[GoToStep("step_3")])
def step_2(number: int) -> None:
    print("Hello, I am step 2")
    raise GoToStep("step_3", retval=2)

@workflow.step(label="step_5")
def step_5() -> None:
    print("Hello, I am step 5")
    raise GoToEnd

@workflow.step(label="step_3")
def step_3(number: int) -> int:
    print("Hello, I am step 3")
    return 3

@workflow.step(paths=[GoToStep("step_5"), GoToEnd()])
def step_4(number: int) -> int:
    print("Hello, I am step 4")
    if number % 2:
        raise GoToStep("step_5", retval=4)
    if number > 6:
        raise GoToEnd
    return 4

@workflow.step
def step_6(number: int) -> int:
    print("Hello, I am step 6")
    return 6

@workflow.step
def step_7(number: int) -> int:
    print("Hello, I am step 7")
    return 7
```

TODO: write description from here.

Calculating the path from `step_1`, it will calculate `('step_1', 'step_2', 'step_3', 'step_4')` and then reach a 
branching of the paths.  It will then calculate two potential routes for the remainder, resulting in three possible 
paths:

* `('step_1', 'step_2', 'step_3', 'step_4')`
* `('step_1', 'step_2', 'step_3', 'step_4', 'step_5')`
* `('step_1', 'step_2', 'step_3', 'step_4', 'step_6', 'step_7')`

For calculating `percent_completed` and `total_steps`, it will use the longest of the potential branches.

When `step_4` is reached and completed, it will then reevaluate the branches to determine which were not taken, and 
discard them, leaving only the relevant branch(es) for recalcation and refinement of the `percent_completed` and 
`total_steps` values.

The resulting workflow order from above is:

1. `step_1`
2. `step_2`
3. `step_3`
4. `step_4` (`number == 3`, so `4` is returned)
5. `step_6`
6. `step_7`

Note that the `return` path wasn't explicitly specified for `step_4`, but it is automatically deduced and included from
the function's return type hinting.  If however a work step function ever intentionally returns `None` as a valid 
workflow path, but additionally has `paths` defined for other paths, then `None` must be manually included in the list of 
paths.

For example:

```py title="workflow_with_paths.py"
from ergate import GoToEnd, GoToStep, Workflow
from datetime import date

workflow = Workflow(unique_name="my_third_workflow")

@workflow.step(paths=[GoToStep("weekday"), GoToStep("Saturday")])
def step_1() -> None:
    print("Hello, I am step 1")

    today = date.today()
    
    if today.weekday() < 5:
        print("Today is a weekday.  Do a weekday task.")
        raise GoToStep("weekday")
    if today.weekday() == 5:
        print("Today is a weekday.  Do a Saturday task.")
        raise GoToStep("Saturday")
        
    print("Today is a Sunday.  Nothing to do.")
    return None

@workflow.step
def step_2() -> None:
    print("Hello, I am step 2")
```

In this case, `step_1` can go to two separate `GoToStep` destinations, but also can return `None`.  However,
the `return` path would be ignored due to its `None` type hinting, since `paths` were manually specified.

To rectify this in this specific instance, one should include `None` in the list of `paths`: 
`@workflow.step(paths=[GoToStep("weekday"), GoToStep("Saturday"), None])`

_Nota bene_: this omission would not affect the workflow's operation, and it would still execute nominally.
This only affects the path calculations for predicting completion percentages and total steps.  Further, once the step
is executed, branch calculations for future steps (which are recalculated at each step for and from the current step 
onwards) would regain their accuracy.