# Creating a job

A job in Ergate represents the execution of a workflow. It is represented by the `Job` model, which contains all the necessary information to execute a given workflow.

Ergate receives jobs through the queue implementation you provide when creating the app. Therefore, it is your responsibility to create a `Job` object from the data you receive from the queue.


!!! tip

    Whenever you serialize a `Job` model and put it into the queue, it's recommended that you include all of the model's data in it. Some of the metadata stored in the model is essential for Ergate to work as expected. Many of the model's defaults are only correct when the job is created for the first time.


## Attributes

Here is a summary of all the attributes of the `Job` model.

| Name                 | Type             | Required on initial run | Default          |
|----------------------|------------------|-------------------------|------------------|
| id                   | Any              | N                       | None             |
| workflow_name        | str              | Y                       | -                |
| step_name            | str \| None      | N                       | None             |
| status               | JobStatus        | N                       | JobStatus.QUEUED |
| steps_completed      | int              | N                       | 0                |
| percent_completed    | float            | N                       | 0.0              |
| initial_input_value  | Any              | N                       | None             |
| last_return_value    | Any              | N                       | None             |
| exception_traceback  | str \| None      | N                       | None             |
| user_context         | Any              | N                       | None             |
| requested_start_time | datetime \| None | N                       | None             |



## Example

!!! info

    Ergate's `Job` model is a Pydantic model, so it will try to cast the given values to the expected types. If any of the data provided cannot be cast to the expected type, a `ValidationError` will be raised. Remember that you must handle all exceptions in your queue and state store implementations.

```py title="my_queue.py"
from queue import Queue
from ergate import Job

queue = Queue()

class MyQueue:
    def get_one(self) -> Job:
        serialized_job = queue.get()
        return Job(**serialized_job) # (1)!

    def put(self, job: Job) -> None:
        serialized_job = job.model_dump(mode="json")
        queue.put(serialized_job)
```

1. `**serialized_job` means that we are unpacking the `serialized_job` dictionary into keyword arguments. So, for example, if the dictionary contains a value of `{"workflow_name": "my_workflow"}`, it will be interpreted as `Job(workflow_name="my_workflow")`.


## Challenge

Now that you know all about jobs, we propose you a simple challenge: using the previous examples in the documentation, would you know how to submit a job to the queue before starting the application, so that the workflow we created in the previous section (named `my_first_workflow`) can be executed?

Give it a try and then check our solutions below!


??? success "Solution 1"

    ```py title="app.py"
    from ergate import Ergate
    from my_queue import MyQueue, queue
    from my_state_store import MyStateStore
    from my_workflow import workflow

    app = Ergate(
        queue=MyQueue(),
        state_store=MyStateStore(),
    )
    app.register_workflow(workflow)

    if __name__ == "__main__":
        job = Job(workflow_name="my_first_workflow")
        queue.put(job.model_dump(mode="json")) # (1)!
        app.run()
    ```

    1. In this case, we're creating a `Job` object with the `workflow_name` attribute set to `"my_first_workflow"`. The rest of the attributes are set to their defaults *before* submitting it to the queue, and therefore all of the job data is sent through the queue.


??? success "Solution 2"

    ```py title="app.py"
    from ergate import Ergate
    from my_queue import MyQueue, queue
    from my_state_store import MyStateStore
    from my_workflow import workflow

    app = Ergate(
        queue=MyQueue(),
        state_store=MyStateStore(),
    )
    app.register_workflow(workflow)

    if __name__ == "__main__":
        queue.put({"workflow_name": "my_first_workflow"}) # (1)!
        app.run()
    ```

    1. In this case, we're submitting directly the only required serialized data for a `Job`'s first run. The default values for all the other attributes will be set when our queue implementation receives this data and creates the `Job` object.
