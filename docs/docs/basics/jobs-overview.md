# Jobs overview

In Ergate, a job is an execution of a workflow. It is represented by the `Job` model, which contains all the necessary information to execute a given workflow.


!!! note

    Ergate receives jobs through the queue implementation you provide when creating the app. Therefore, how you trigger jobs and create `Job` objects depends only on your queue implementation. In this guide, we'll show you how to create a `Job` object and submit it to the queue using the queue implementation from the previous sections.


## Job attributes

Here is a summary of all the attributes of the `Job` model.

| Name                 | Type             | Required | Default          | User provided |
|----------------------|------------------|----------|------------------|---------------|
| id                   | Any              | N        | None             | Y             |
| workflow_name        | str              | Y        | N/A              | Y             |
| status               | JobStatus        | N        | JobStatus.QUEUED | N             |
| steps_completed      | int              | N        | 0                | N             |
| percent_completed    | float            | N        | 0.0              | N             |
| initial_input_value  | Any              | N        | None             | Y             |
| last_return_value    | Any              | N        | None             | N             |
| user_context         | Any              | N        | None             | Y             |
| requested_start_time | datetime \| None | N        | None             | Y             |


## Job status

A `Job` can have any of the following statuses:

- `JobStatus.SCHEDULED`
- `JobStatus.QUEUED`
- `JobStatus.RUNNING`
- `JobStatus.COMPLETED`
- `JobStatus.FAILED`
- `JobStatus.ABORTED`


## Triggering/creating a job

Triggering/creating a job is extremely simple. All you need to do it to submit the necessary data to the queue which your queue implementation will later consume to create a `Job` object. There is two ways to do this:

1. Create a `Job` object on the client, and then dump all of its data into the queue.
1. Submit only the necessary data for a `Job`'s first run from the client into the queue, and let the queue implementation create the `Job` object with the default values for all the other fields.

!!! info

    Our recommendation is to always use the first approach. The `Job` model's default values are only valid before the job's first run. After that, the job's metadata (`steps_completed`, `percent_completed`, etc...) is updated by Ergate, and it will no longer be valid to use the default values for subsequent runs, which means you will need to submit all of the data through the queue so it can be loaded in the next steps.

    By using the first approach, not only can you validate data before submitting it to the queue (since the model will raise a `ValidationError` if it's initialized with invalid values), but you can also ensure that all the job-related data sent through the queue remains consistent; regardless of whether it's the first run or a subsequent run of the job.

    Throughout this documentation we will only demonstrate the first approach.

---

We now propose you a simple challenge: modify the code from the previous sections so a new job gets submitted to the queue just before starting the app. The job must trigger the workflow named `my_first_workflow`. Give it a try and then check our solution below!


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
        job = Job(workflow_name="my_first_workflow") # (1)!
        queue.put(job.model_dump(mode="json")) # (2)!
        app.run()
    ```

    1. Here we're creating the `Job` object for the workflow named `my_first_workflow`...
    2. ...and here we're converting it to JSON and submitting that JSON payload to the queue
