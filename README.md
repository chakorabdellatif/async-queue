# async-queue

> A structured self-study path to understand **Distributed Systems** from the ground up, starting with async execution and message queues — capped with one real mini-project.

---

## Why this exists

Distributed systems are hard to learn in the abstract. This repo takes a concrete path:

1. Understand the theory behind async execution and queues
2. Get hands-on with the right tools
3. Build one mini-project that ties it all together

Stack: **FastAPI · Celery · Redis · Docker**

---

## Roadmap

### Phase 1 — Core concepts

#### Async systems

- **Sync vs async execution** — what does "blocking" actually mean? Why does a thread waiting on I/O waste resources?
- **Event loop** — how Python's `asyncio` loop works: one thread, many coroutines, cooperative scheduling
- **Concurrency vs parallelism** — concurrency is about structure (doing many things at once via switching), parallelism is about execution (doing many things truly simultaneously). You need both concepts.
- **`async`/`await` in Python** — coroutines, `await`-able objects, `asyncio.gather`, `asyncio.Queue`
- **I/O-bound vs CPU-bound** — async shines for I/O-bound tasks (network, disk). CPU-bound needs multiprocessing or workers.

Key question to be able to answer: *"Why doesn't `time.sleep()` work inside an async function?"*

#### Message queues

- **Producer / consumer model** — decoupling the thing that creates work from the thing that does work
- **Message broker** — a middleman (Redis, RabbitMQ, Kafka) that holds messages until a consumer picks them up
- **Queue vs pub/sub** — queue: one message, one consumer. pub/sub: one message, many subscribers.
- **Acknowledgement (ACK)** — a consumer tells the broker "I processed this, you can remove it"
- **Dead letter queue (DLQ)** — where messages go when they fail too many times
- **Backpressure** — what happens when consumers are slower than producers? How do you not explode?
- **Delivery guarantees:**
  - *At-most-once* — fire and forget, may lose messages
  - *At-least-once* — retried until ACK'd, may process duplicates
  - *Exactly-once* — hardest to achieve, requires idempotent consumers

Key question to be able to answer: *"If your worker crashes mid-task, what happens to the message?"*

#### Kafka
- Topics, partitions, offsets
- Consumer groups and how multiple consumers share work
- Why Kafka is a log, not a traditional queue
- When to choose Kafka over Redis/RabbitMQ

> No hands-on Kafka in this repo. It deserves its own dedicated project once the fundamentals are solid.

---

### Phase 2 — Tech stack

#### FastAPI
- `async def` route handlers and why they matter for throughput
- Background tasks with `BackgroundTasks`
- Dependency injection pattern
- Pydantic models for request/response validation
- Running with `uvicorn` (ASGI server)

#### Redis
- Data structures: strings, lists, hashes, streams
- Redis as a **cache** — TTL, cache-aside pattern, cache invalidation
- Redis as a **broker** — how Celery uses Redis lists as queues
- Redis Streams (bonus) — persistent, consumer-group-aware message log

#### Celery
- Tasks, workers, and the broker connection
- `@app.task` decorator and calling tasks with `.delay()` / `.apply_async()`
- Task retries with exponential backoff
- `eta` and `countdown` for delayed execution
- Celery Beat for scheduled/periodic tasks
- Flower — the web UI to monitor workers and tasks

#### Docker
- Writing a `Dockerfile` for a Python app
- `docker-compose.yml` to wire up FastAPI + Celery worker + Redis together
- Health checks and service dependencies
- Volume mounts for local development

---

### Phase 3 — Mini-project

#### Background job processor — async task API

A simple but complete system where a user submits a job via HTTP, the job is processed asynchronously in the background, and the user can poll for the result.

**What it covers:**
- Async FastAPI endpoints (submit job, check status, get result)
- Redis as both the Celery broker and the result cache
- Celery worker picking up jobs from the queue
- Task retry on failure with backoff
- Job status stored in Redis: `pending → processing → done / failed`
- Everything wired together with Docker Compose

**Folder structure:**
```
async-queue-lab/
├── app/
│   ├── main.py          # FastAPI: POST /jobs, GET /jobs/{id}
│   ├── tasks.py         # Celery task definitions
│   ├── celery_app.py    # Celery + Redis config
│   └── schemas.py       # Pydantic models
├── docker-compose.yml   # FastAPI + worker + Redis
├── Dockerfile
└── requirements.txt
```

**The one flow to understand:**
```
POST /jobs
  → FastAPI enqueues task via Celery (.delay())
  → returns job_id immediately (non-blocking)

Celery worker (separate process)
  → picks up task from Redis queue
  → processes it (simulate with time.sleep or real work)
  → stores result in Redis with job_id as key

GET /jobs/{job_id}
  → FastAPI reads status/result from Redis
  → returns current state to client
```

**Milestones:**
1. Get Redis + Celery worker running with Docker Compose
2. Write one Celery task that simulates work and stores a result
3. Wire up FastAPI: submit endpoint returns a `job_id`, status endpoint reads from Redis
4. Add retry logic: if the task raises an exception, retry up to 3 times with backoff
5. Open Flower and watch your tasks flow through in real time

---

### Phase 4 — Production hardening

- **Idempotent consumers** — if a task runs twice (due to retry), the result should be the same. Design tasks to be safe to re-run.
- **Structured logging** — every log line includes `job_id`, `worker_id`, timestamp. No naked `print()`.
- **Prometheus metrics** — queue depth, task duration, failure rate. Add `prometheus_client` to the worker.
- **Graceful shutdown** — what happens to in-flight tasks when you `docker stop` a worker?
- **Schema validation on messages** — don't let a malformed payload crash your worker silently.

---

## Resources

| Topic | Resource |
|---|---|
| Python asyncio | [docs.python.org/3/library/asyncio](https://docs.python.org/3/library/asyncio.html) |
| FastAPI | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| Celery | [docs.celeryq.dev](https://docs.celeryq.dev) |
| Redis | [redis.io/docs](https://redis.io/docs/) |
| Distributed systems primer | *Designing Data-Intensive Applications* — Kleppmann (ch. 1–2 to start) |

---

## Repo name

`async-queue-lab`