# Defining workflow paths

In order to facilitate manually-ordered workflow steps with branching paths, speculative logic was included to predict 
the total number of steps for the workflow and thereby calculate the completion percentage.

These may be seen as similar to Python type hints, in that they do not directly affect the flow and operation of the 
workflow, but provide metadata allowing the engine to better determine information about the workflow operation, viz. the
completion percentage and total steps.

This logic may be enabled by specifying the `paths=` kwarg for a given `@workflow.step()` decorator.

* It is not necessary to specify `paths` for workflow steps which only return a value via `return`.
* It is suggested to define `paths` for steps which utilise the `SkipNSteps` or `GoToEnd` exceptions. 
* It is recommended to define `paths` for steps which utilise the `GoToStep` exception, or which have branching logic with multiple potential paths.

`paths` may be freely defined alongside other kwargs in the `@workflow.step` decorator.

## Defining workflow paths
When defining `paths`, each potential path should be specified by its Exception.

```py title="workflow_with_paths.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="workflow_with_paths")

@workflow.step
def step_1() -> int:
    print("Hello, I am step 1")
    return 1

@workflow.step(paths=[GoToStepPath("step_3")])
def step_2(number: int) -> None:
    print("Hello, I am step 2")
    raise GoToStep(step_3, retval=2)

@workflow.step(path=[GoToEndPath()])
def step_5() -> None:
    print("Hello, I am step 5")
    raise GoToEnd()

@workflow.step
def step_3(number: int) -> int:
    print("Hello, I am step 3")
    return 3

@workflow.step(paths=[GoToStepPath("step_7"), GoToEndPath()])
def step_4(number: int) -> int:
    print("Hello, I am step 4")
    if number % 2:
        raise GoToStep(step_7, retval=4)
    if number > 6:
        raise GoToEnd()
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

Calculating the path from `step_1`, it will calculate `('step_1', 'step_2', 'step_3', 'step_4')` and then reach a 
branching of the paths.  It will then calculate two potential routes for the remainder, resulting in three possible 
paths:

* `('step_1', 'step_2', 'step_3', 'step_4')`
* `('step_1', 'step_2', 'step_3', 'step_4', 'step_7')`
* `('step_1', 'step_2', 'step_3', 'step_4', 'step_6', 'step_7')`

For calculating `percent_completed` and `total_steps`, it will use the longest of the potential branches.

When `step_4` is reached and completed, it will then reevaluate the branches to determine which were not taken, and 
discard them, leaving only the relevant branch(es) for recalculation and refinement of the `percent_completed` and 
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
workflow path, but additionally has `paths` defined for other paths, then `NextSteppath()` must be manually included in 
the list of paths.

For example:

```py title="workflow_with_paths_2.py"
from ergate import GoToEnd, GoToEndPath, GoToStep, GoToStepPath, Workflow
from datetime import date

workflow = Workflow(unique_name="workflow_with_paths_2")

@workflow.step(paths=[GoToStepPath("step_two")])
def step_one() -> None:
    print("Hello, I am step 1.")
    raise GoToStep(step_two)

@workflow.step(paths=[GoToStepPath("weekday"), GoToStepPath("saturday")])
def step_two() -> None:
    print("Hello, I am step 2.")

    today = date.today()
    
    if today.weekday() < 5:
        print("Today is a weekday.  Do a weekday task.")
        raise GoToStep(weekday)
    if today.weekday() == 5:
        print("Today is Saturday.  Do a Saturday task.")
        raise GoToStep(saturday)
        
    print("Today is a Sunday.  Proceed to the next step.")
    return None

@workflow.step(paths=[GoToStepPath("step_three")])
def sunday() -> None:
    print("Hello, I am Sunday step.")
    raise GoToStep(step_three)

@workflow.step(paths=[GoToStepPath("step_three")])
def weekday() -> None:
    print("Hello, I am the extra weekday step.")
    raise GoToStep(step_three)

@workflow.step(paths=[GoToStepPath("step_three")])
def saturday() -> None:
    print("Hello, I am the extra saturday step.")
    raise GoToStep(step_three)

@workflow.step
def step_three() -> None:
    print("Hello, I am step 3.")

```

In this case, `step_two` can go to two separate `GoToStep` destinations, but also can return `None`.  However, the 
natural `return` path would be ignored due to its `None` type hinting, since `paths` were manually specified.

To rectify this in this specific instance, one should include `NextStepPath()` in the list of `paths`: 
`@workflow.step(paths=[GoToStepPath("weekday"), GoToStepPath("saturday"), NextStepPath()])`

Steps were organised in such a way to prevent the natural sequencing of `step_two` or `step_three` from inadvertently 
executing named steps for specific conditions, by placing those conditional steps subsequent to a `GoToStep` step. 

_Nota bene_: the omission of `NextStepPath()` from the `paths` would not affect the workflow's operation, and it would 
still execute nominally.  This only affects the path calculations for predicting completion percentages and total steps.  
Further, once the step is executed, branch calculations for future steps (which are recalculated at each step for and 
from the current step onwards) would regain their accuracy.
