# I/O-bound vs CPU-bound

> [!NOTE]
> Why This Distinction Is Extremely Important: One of the biggest mistakes in distributed systems is using the wrong concurrency model for the workload. 

## Table of Contents
- [The Core Difference](#the-core-difference)
- [Visual Comparison](#visual-comparison)
- [Why Async Works for I/O-bound Tasks](#why-async-works-for-io-bound-tasks)
- [Executable Examples](#executable-examples)
  - [I/O-bound Example](#io-bound-example)
  - [CPU-bound Example](#cpu-bound-example)
- [Correct Solution for CPU-bound Work](#correct-solution-for-cpu-bound-work)
- [Distributed Systems Perspective](#distributed-systems-perspective)
  - [Real Production Example — YouTube](#real-production-example--youtube)
  - [Real Production Example — Chat Application](#real-production-example--chat-application)
- [Final Mental Model](#final-mental-model)

Before choosing `asyncio`, threads, `multiprocessing`, worker queues, or distributed workers, you must first answer: **Is this workload I/O-bound or CPU-bound?** This determines scalability, performance, architecture, and infrastructure cost.

---

## The Core Difference

| Type | Main Bottleneck |
| :--- | :--- |
| **I/O-bound** | Waiting |
| **CPU-bound** | Computation |

### I/O-bound Tasks
An I/O-bound task spends most of its time waiting for network responses, database queries, files, APIs, or message brokers. The CPU is mostly idle.

> [!TIP]
> **Analogy:** A waiter in a restaurant takes an order, waits for the kitchen, and serves the customer. Most time is waiting.

### CPU-bound Tasks
A CPU-bound task spends most of its time performing calculations, processing data, running algorithms, compressing files, or training models. The CPU is heavily utilized.

> [!TIP]
> **Analogy:** A chef preparing food is chopping, cooking, mixing, and baking. Most time is active work.

---

## Visual Comparison

**I/O-bound**
```text
CPU Work:     ██
Waiting Time: ████████████████████
```
*Most time is spent waiting.*

**CPU-bound**
```text
CPU Work:     ████████████████████
Waiting Time: ██
```
*Most time is spent computing.*

---

## Why Async Works for I/O-bound Tasks

Suppose an API request waits 2 seconds for a database.
- **Without async:** CPU sits idle for 2 seconds.
- **With async:** CPU handles other requests meanwhile. 
This massively improves throughput.

### Why Async Does NOT Help CPU-bound Tasks
Suppose a task performs heavy computation in a `for` loop. There is no waiting, no yielding, no I/O pause. The CPU is fully busy. Async cannot magically speed this up.

> [!IMPORTANT]
> **Important Rule:** Async solves *waiting* problems. NOT computation problems.

---

## Executable Examples

### I/O-bound Example
This demonstrates why async is powerful for waiting tasks.

```python
import asyncio
import time

async def fetch_data(name, delay):
    print(f"{name}: Starting request")
    await asyncio.sleep(delay)
    print(f"{name}: Response received")

async def main():
    start = time.time()
    await asyncio.gather(
        fetch_data("Service A", 2),
        fetch_data("Service B", 2),
        fetch_data("Service C", 2),
    )
    end = time.time()
    print(f"\nTotal Time: {end - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```
**Expected Output:**
```text
Service A: Starting request
...
Total Time: 2.00 seconds
```
**Why Was It Fast?** All tasks spend most time waiting, the event loop switches between them, and the waiting overlaps. (Sequential execution would take 6.00 seconds).

### CPU-bound Example
Now look at CPU-heavy computation.

```python
import time

def cpu_heavy_task(name):
    print(f"{name}: Starting computation")
    result = 0
    for i in range(50_000_000):
        result += i * i
    print(f"{name}: Finished computation")

start = time.time()
cpu_heavy_task("Task A")
cpu_heavy_task("Task B")
end = time.time()

print(f"\nTotal Time: {end - start:.2f} seconds")
```
**What Happens?** The CPU becomes fully occupied. No waiting exists. 

> [!WARNING]
> **Event Loop Freezing**
> Trying to run CPU-heavy tasks concurrently using `asyncio` blocks the event loop. No yielding occurs, so other async tasks freeze. This is a common production mistake.

---

## Correct Solution for CPU-bound Work

Use:
- `multiprocessing`
- worker queues
- distributed workers
- separate compute services

### Multiprocessing Example
```python
import multiprocessing
import time

def cpu_task(name):
    print(f"{name}: Starting")
    result = 0
    for i in range(50_000_000):
        result += i * i
    print(f"{name}: Finished")

if __name__ == "__main__":
    start = time.time()
    p1 = multiprocessing.Process(target=cpu_task, args=("Task A",))
    p2 = multiprocessing.Process(target=cpu_task, args=("Task B",))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    end = time.time()

    print(f"\nTotal Time: {end - start:.2f} seconds")
```
**Why Multiprocessing Works:** Multiple OS processes use multiple CPU cores to achieve true parallel execution. Now CPU-heavy work scales correctly.

---

## Distributed Systems Perspective

Modern distributed systems separate workloads by type.

### I/O-bound Services
Usually async. 
- **Examples:** API gateways, chat servers, WebSocket servers, proxies, microservices.
- **Technologies:** FastAPI, Node.js, NGINX, asyncio, Go.

### CPU-bound Services
Usually parallel/distributed.
- **Examples:** video transcoding, AI inference, ML training, image processing, analytics engines.
- **Technologies:** multiprocessing, Spark, Ray, CUDA, Rust/C++.

### Real Production Example — YouTube
- **I/O-bound Layer:** Handles uploads, metadata, comments. Mostly waiting on databases and network. Async works perfectly.
- **CPU-bound Layer:** Handles video compression, encoding. Requires heavy computation (GPU/CPU clusters). Async alone would fail badly here.

### Real Production Example — Chat Application
- **I/O-bound:** Chat server waiting for websocket messages and Redis. One event loop can handle thousands of users.
- **CPU-bound:** Voice/video processing, noise suppression, encoding. Requires parallel processing.

---

## Final Mental Model

| Workload | Best Solution |
| :--- | :--- |
| HTTP APIs, Databases, WebSockets, Kafka | Async |
| Machine learning, Image rendering, Encryption | Parallelism |

> [!TIP]
> **Most Distributed Systems Are Mostly I/O-bound**
> Microservices constantly communicate over networks, call APIs, and access databases. That is why async architectures became dominant. Modern systems often use a **Hybrid Architecture**: an Async Frontend Layer for requests, and a Multiprocessing Worker Layer for heavy computation.

- **I/O-bound:** "The system spends most of its time waiting." -> Use async, event loops, concurrency.
- **CPU-bound:** "The system spends most of its time computing." -> Use parallelism, multiprocessing, distributed workers.

### Ultimate Rule
**Async Helps When Tasks WAIT.**  
**Parallelism Helps When Tasks COMPUTE.**

Understanding this distinction is foundational for designing scalable distributed systems.
