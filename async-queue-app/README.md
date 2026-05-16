# async-queue-lab 

Background job processor built with **FastAPI · Celery · Redis · Docker**.  
Submit a job over HTTP, get a `job_id` back instantly, poll for the result.

---

## Stack

| Service | Role |
|---|---|
| FastAPI | HTTP API — submit jobs, poll status |
| Celery | Worker — picks up and processes jobs |
| Redis | Broker (task queue) + result store |
| Flower | Web UI to monitor workers and tasks |

---

## Start

```bash
docker compose up --build
```

| URL | What |
|---|---|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:5555 | Flower (task monitor) |

---

## Usage

**Submit a job**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"job_type": "process_data", "payload": {"rows": 1000}}'
```
```json
{ "job_id": "abc-123", "status": "pending" }
```

**Poll for result**
```bash
curl http://localhost:8000/jobs/abc-123
```
```json
{ "job_id": "abc-123", "status": "done", "result": { "rows_processed": 1000 } }
```

---

## Job types

| `job_type` | What it teaches |
|---|---|
| `process_data` | Normal async job, always succeeds |
| `send_report` | Slow external call — why async decouples latency |
| `flaky_job` | Randomly fails — watch **retries** in Flower |

---

## Scale workers

```bash
docker compose up --scale worker=3
```

---

## Project structure

```
app/
├── app/
│   ├── celery_app.py   # Celery + Redis config
│   ├── main.py         # FastAPI endpoints
│   ├── schemas.py      # Pydantic models
│   └── tasks.py        # Task definitions + retry logic
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
