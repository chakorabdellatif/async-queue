# Celery Architecture

> [!NOTE]  
> Celery is not a message broker itself; it is a **Distributed Task Queue framework** written in Python. It provides the abstractions to easily write tasks, send them, and run workers that consume them. 

## Concept Explanation

Celery requires an external message broker (like RabbitMQ or Redis) to actually transport the messages. It handles the complexity of polling the broker, managing worker processes (using pre-forking, gevent, or eventlet), handling retries, and writing results to a backend.

## Architecture & Components

1. **Client (Producer):** The web application (e.g., FastAPI/Django) that calls `task.delay()`.
2. **Broker:** The middleman (RabbitMQ or Redis) that stores the task payload.
3. **Workers (Consumers):** Celery processes running in the background, constantly pulling from the broker.
4. **Result Backend (Optional):** A database or cache (Redis/Postgres) where workers store the return value of a task so the client can check the status later.

## Celery Workflow Diagram

```mermaid
graph TD
    C[FastAPI App (Producer)] -->|task.delay()| B((Broker: RabbitMQ / Redis))
    B -->|Fetch Task| W[Celery Worker]
    W -->|Save Result| R[(Result Backend: Redis)]
    C -.->|Check Status| R
```
