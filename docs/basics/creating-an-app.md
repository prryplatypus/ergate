# Creating an app

Creating an Ergate application is simple, but you must first create our own queue and state store implementations for Ergate to be able to receive and process jobs.


!!! warning
    You are responsible for handling any exceptions within your queue and state store implementations. Ergate will not handle any exceptions that occur within these classes, and they will crash your application.

## Implementing the queue

Ergate requires queue implementations to implement two methods: `get_one` and `put`.

- The `get_one` method should fetch data from your queue and return a `Job` instance. If no job data is found instantly in the queue, this method should block until it is available, at which point it will return a `Job`.

- The `put` method takes a `Job` model and should put its data back into the queue. This method is called after each step is completed if the job hasn't reached a final state, so that other workers can pick up the data and continue processing the next step in the job.

Let's create a simple queue implementation using Python's built-in `Queue` class. In this example, our queue will expect JSON data to be submitted through it.

```py title="my_queue.py"
from queue import Queue
from ergate import Job

queue = Queue() # (1)!

class MyQueue:
    def get_one(self) -> Job:
        serialized_job = queue.get()
        return Job(**serialized_job)

    def put(self, job: Job) -> None:
        serialized_job = job.model_dump(mode="json")
        queue.put(serialized_job)
```

1. In practice, you would likely use a distributed queue implementation, such as Kafka or RabbitMQ.


## Implementing the state store

Ergate requires state store implementations to implement one method: `update`.

- The `update` method takes a `Job` model and should update the state of the job in your state store. It is called just before a step is executed and after a step execution is completed.

Let's create a simple state store implementation in which we'll be sending a `PATCH` request to an API endpoint with the new job's state.

```py title="my_state_store.py"
import requests
from ergate import Job

class MyStateStore:
    def update(self, job: Job) -> None:
        requests.patch("https://example.com", json=job.model_dump(mode="json"))
```


## Connecting everything together

Now that we have our queue and state store implementations, we can finally create the application itself. Simply create an `Ergate` instance and pass in the queue and state store implementations that you created before.

To run it, simply call the `run` method on the app instance. This will start the application and begin processing jobs.

!!! info

    Running this will make the app appear "stuck". The reason for this is that there's no jobs in the queue. However, it would be pointless to have any, as we have not defined any workflows yet. We'll cover that in the next section.

```py title="app.py"
from ergate import Ergate
from my_queue import MyQueue
from my_state_store import MyStateStore

app = Ergate(
    queue=MyQueue(),
    state_store=MyStateStore(),
)

if __name__ == "__main__":
    app.run()
```
