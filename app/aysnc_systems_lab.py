# =========================================================
# ASYNC SYSTEMS NOTES
# =========================================================

# ---------------------------------------------------------
# 1. IO-BOUND vs CPU-BOUND
# ---------------------------------------------------------

# IO-BOUND:
# The program spends most of its time WAITING.
# Examples:
# - API requests
# - Database queries
# - File reading/writing
# - Network operations

# CPU-BOUND:
# The program spends most of its time COMPUTING.
# Examples:
# - Model training
# - Data processing
# - Image/video processing
# - Heavy calculations


# ---------------------------------------------------------
# 2. SYNCHRONOUS vs ASYNCHRONOUS
# ---------------------------------------------------------

# SYNCHRONOUS:
# Tasks execute one after another.
#
# Example:
# Task A -> finishes
# then
# Task B -> starts

# ASYNCHRONOUS:
# Tasks can overlap.
# While one task waits for I/O,
# another task can run.
#
# Improves:
# - scalability
# - latency
# - resource efficiency

# Async systems are mainly designed for IO-bound workloads.


# ---------------------------------------------------------
# 3. EVENT LOOP (Engine of Async)
# ---------------------------------------------------------

# The event loop manages async tasks.

# HOW IT WORKS:

# 1. Task Queue
# The loop keeps a queue of ready tasks.

# 2. Execution
# It runs a task until the task hits `await`.

# 3. Suspension
# The task pauses.
# The loop waits for the I/O event to complete.

# 4. Resumption
# Once the I/O completes,
# the task goes back into the queue
# and resumes where it stopped.


# ---------------------------------------------------------
# 4. ASYNCIO
# ---------------------------------------------------------

# asyncio:
# Python built-in library for asynchronous programming.


# ---------------------------------------------------------
# 5. CORE ASYNC KEYWORDS
# ---------------------------------------------------------

# async def
# Defines an asynchronous function (coroutine).

# await
# Pauses the current task,
# while allowing other tasks to run.

# asyncio.run()
# Starts the event loop.


# ---------------------------------------------------------
# 6. asyncio.gather()
# ---------------------------------------------------------

# asyncio.gather(task1(), task2())

# Purpose:
# Run multiple async tasks together
# and wait until ALL finish.

# Result:
# Total execution time ~= longest task only.


# ---------------------------------------------------------
# 7. asyncio.create_task()
# ---------------------------------------------------------

# asyncio.create_task(worker())

# Purpose:
# Start a task independently in the background.

# Useful when:
# - tasks should run independently
# - you want to await later
# - background jobs are needed


# ---------------------------------------------------------
# 8. PARALLELISM
# ---------------------------------------------------------

# Parallelism:
# Multiple tasks execute at the EXACT same moment.

# Requires:
# - multiple CPU cores
# - multiple machines
# - distributed workers

# Common tools:
# - multiprocessing
# - ProcessPoolExecutor


# ---------------------------------------------------------
# 9. DISTRIBUTED SYSTEMS
# ---------------------------------------------------------

# Common architecture:

# asyncio
# -> handles networking / IO-bound tasks

# multiprocessing
# -> handles CPU-heavy tasks

# Together:
# Efficient distributed systems.


"""
ASYNCIO MINI CLASS
"""

import asyncio
import time
from multiprocessing import Process


# =========================================================
# 1. SYNCHRONOUS
# =========================================================
# Tasks execute one after another.
# Total time = sum of all task times.


def sync_task(name, delay):
    print(f"{name} started")
    time.sleep(delay)  # BLOCKS the whole program
    print(f"{name} finished")


def synchronous_example():
    print("\n--- SYNCHRONOUS ---")

    start = time.time()

    sync_task("A", 2)
    sync_task("B", 1)

    end = time.time()

    print(f"Total time: {end - start:.2f}s")


# =========================================================
# 2. ASYNCHRONOUS
# =========================================================
# Tasks can overlap while waiting.
# Great for IO-bound tasks:
# - API calls
# - DB queries
# - File/network waiting


async def async_task(name, delay):
    print(f"{name} started")

    # NON-BLOCKING WAIT
    # gives control back to event loop
    await asyncio.sleep(delay)

    print(f"{name} finished")


async def asynchronous_example():
    print("\n--- ASYNCHRONOUS + GATHER ---")

    start = time.time()

    # Runs BOTH together
    await asyncio.gather(
        async_task("A", 2),
        async_task("B", 1),
    )

    end = time.time()

    # total time ~= longest task only
    print(f"Total time: {end - start:.2f}s")


# =========================================================
# 3. create_task()
# =========================================================
# Start task in background.
# Useful when task should run independently.


async def background_worker():
    print("Background task started")

    await asyncio.sleep(3)

    print("Background task finished")


async def create_task_example():
    print("\n--- CREATE_TASK ---")

    # starts immediately in background
    task = asyncio.create_task(background_worker())

    print("Main continues running...")

    await asyncio.sleep(1)

    print("Main still doing work...")

    # wait for background task
    await task


# =========================================================
# 4. EVENT LOOP CONCEPT
# =========================================================
# How it works:
#
# Task A starts
# -> hits await
# -> pauses
#
# Event loop switches to Task B
#
# Once A finishes waiting,
# event loop resumes A.


async def loop_demo(name):
    print(f"{name}: step 1")

    await asyncio.sleep(2)

    print(f"{name}: step 2")


async def event_loop_example():
    print("\n--- EVENT LOOP ---")

    await asyncio.gather(
        loop_demo("Task-A"),
        loop_demo("Task-B"),
    )


# =========================================================
# 5. CPU-BOUND TASK
# =========================================================
# Heavy computation.
# BAD for asyncio directly.
#
# Example:
# - model training
# - image processing
# - huge calculations


def cpu_heavy():
    print("CPU task started")

    total = 0

    for i in range(50_000_000):
        total += i

    print("CPU task finished")


def cpu_bound_example():
    print("\n--- CPU-BOUND ---")

    start = time.time()

    cpu_heavy()

    end = time.time()

    print(f"Total time: {end - start:.2f}s")


# =========================================================
# 6. PARALLELISM (multiprocessing)
# =========================================================
# TRUE parallel execution.
# Uses multiple CPU cores.
#
# Unlike asyncio:
# tasks REALLY run simultaneously.


def parallel_worker(name):
    print(f"{name} started")

    total = 0

    for i in range(30_000_000):
        total += i

    print(f"{name} finished")


def multiprocessing_example():
    print("\n--- MULTIPROCESSING / PARALLELISM ---")

    start = time.time()

    p1 = Process(target=parallel_worker, args=("P1",))
    p2 = Process(target=parallel_worker, args=("P2",))

    # start both processes
    p1.start()
    p2.start()

    # wait for both
    p1.join()
    p2.join()

    end = time.time()

    print(f"Total time: {end - start:.2f}s")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    # 1. synchronous
    synchronous_example()

    # 2. async gather
    asyncio.run(asynchronous_example())

    # 3. create_task
    asyncio.run(create_task_example())

    # 4. event loop
    asyncio.run(event_loop_example())

    # 5. cpu-bound
    cpu_bound_example()

    # 6. multiprocessing
    multiprocessing_example()
