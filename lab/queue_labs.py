# ============================================================
# 📦  MESSAGE QUEUES — FULL STUDY NOTES
# ============================================================
# A self-contained Python "class" used purely as an
# organised container for theory.  Every section is a
# @staticmethod so you can call it to print a quick recap,
# but the real value is in reading the docstrings / comments.
# ============================================================


class MessageQueuesNotes:
    """
    ================================================================
    WHAT IS A MESSAGE QUEUE SYSTEM?
    ================================================================
    A Message Queue is a form of asynchronous communication between
    services.  A Producer sends messages into a queue/broker; a
    Consumer reads them independently.

    Core idea: DECOUPLE the writer from the reader so neither has
    to wait on the other.

    Popular tools
    -------------
      - RabbitMQ  → classic AMQP broker, great for task queues
      - Redis     → in-memory broker / cache hybrid (via Redis Streams
                    or the older List-based approach)
      - Kafka     → distributed event-streaming log, built for
                    massive throughput & replay
      - Celery    → Python worker framework that sits ON TOP of a
                    broker (usually RabbitMQ or Redis)
    ================================================================
    """

    # ----------------------------------------------------------------
    # 1.  PRODUCER / CONSUMER MODEL
    # ----------------------------------------------------------------
    @staticmethod
    def producer_consumer():
        """
        PRODUCER / CONSUMER MODEL
        ==========================
        Producer  →  creates messages / jobs and drops them in a queue.
        Consumer  →  independently reads from the queue and does the work.

        Why bother?
        -----------
        - The producer doesn't wait for the consumer to finish
          → faster HTTP responses for the end-user.
        - Each side scales independently.
        - A crash on one side doesn't bring the other down.

        Real-world example
        ------------------
        E-commerce checkout:
          1. Web server (Producer) receives "Buy Now".
          2. Instantly pushes  {"order_id": 123, "action": "send_email"}
             to the queue and returns HTTP 200 to the browser.
          3. Email workers (Consumers) pick the message up in the
             background and send the confirmation — no user waiting!

        Diagram
        -------
          Producer (Web Server)
               |
               v
          [  Message Queue  ]
               |        |        |
               v        v        v
           Worker1   Worker2   Worker3
        """

    # ----------------------------------------------------------------
    # 2.  MESSAGE BROKER
    # ----------------------------------------------------------------
    @staticmethod
    def message_broker():
        """
        MESSAGE BROKER
        ==============
        An intermediary server that routes, stores, and delivers messages.
        Think of it as the "post office" of your distributed system.

        Responsibilities
        ----------------
        - Persist messages to disk (survive restarts).
        - Route messages to the right queue / topic.
        - Handle retries, timeouts, and dead-lettering.
        - Language-agnostic: Python producer → Java consumer ✓

        Real-world example
        ------------------
        Microservices resilience:
          - "Order Service" sends a payment message while
            "Payment Service" is down.
          - Broker holds the message safely on disk.
          - When Payment Service recovers it drains the backlog —
            zero data loss.

        Diagram
        -------
          Service A ──┐
                      ├──► [ Message Broker ] ──► Service D
          Service C ──┘                       └──► Service E

        Tools: RabbitMQ, Kafka, AWS SQS, Google Pub/Sub
        """

    # ----------------------------------------------------------------
    # 3.  QUEUE vs PUB/SUB
    # ----------------------------------------------------------------
    @staticmethod
    def queue_vs_pubsub():
        """
        QUEUE (Point-to-Point)  vs  PUB/SUB (Broadcast)
        =================================================

        ┌─────────────────────────────────────────────────────────┐
        │  QUEUE (Point-to-Point)                                 │
        │  ─────────────────────                                  │
        │  • Message → one consumer only.                         │
        │  • Even with 10 workers, only ONE gets each message.    │
        │  • Use-case: task distribution                          │
        │    → Video encoding: 1 video ÷ 1 server (not 5 servers │
        │      encoding the same file simultaneously).            │
        └─────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────┐
        │  PUB/SUB (Publish / Subscribe)                          │
        │  ─────────────────────────────                          │
        │  • Message → ALL subscribers on that topic.             │
        │  • Use-case: event broadcasting                         │
        │    → "user_created" event fires once:                   │
        │        Email Service  → sends welcome email             │
        │        Analytics Svc  → updates metrics                 │
        │        CRM Service    → creates profile                 │
        └─────────────────────────────────────────────────────────┘

        Diagram
        -------
          QUEUE                          PUB/SUB
          ─────                          ───────
          Producer                       Publisher
              │                              │
              ▼                              ▼
          [ Queue ]                      ((Topic))
           /     \                      /    |    \.
        Worker A  Worker B         Svc X  Svc Y  Svc Z
        (msg 1)  (msg 2)           (all)  (all)  (all)

        RabbitMQ supports both via "direct" (queue) & "fanout" exchanges.
        Kafka is natively Pub/Sub but consumers in the same group
        behave like a queue.
        """

    # ----------------------------------------------------------------
    # 4.  ACKNOWLEDGEMENT (ACK)
    # ----------------------------------------------------------------
    @staticmethod
    def acknowledgement():
        """
        ACKNOWLEDGEMENT (ACK)
        =====================
        A signal sent FROM the consumer TO the broker confirming
        "I finished processing this message — you can delete it."

        Lifecycle
        ---------
        1. Broker delivers message → marks it "un-acked / in-flight".
        2a. Worker finishes → sends ACK → broker deletes message. ✓
        2b. Worker crashes  → connection times out → broker RE-QUEUES
            the message so another worker can retry it.            ✓

        Real-world example
        ------------------
        Resilient payment refund:
          - Worker picks up "process_refund", calls bank API.
          - Server loses power mid-call.
          - No ACK was sent → broker detects timeout.
          - Message is re-queued → another worker finishes the refund.
          → Financial consistency preserved!

        Sequence diagram
        ----------------
          Broker ──► Consumer : deliver msg (mark un-acked)
          Consumer             : processing…
          Consumer ──► Broker  : ACK
          Broker               : safely delete message

          Broker ──► Consumer : deliver msg2 (mark un-acked)
          Consumer             : CRASH 💥
          Broker               : timeout detected → re-queue msg2
        """

    # ----------------------------------------------------------------
    # 5.  DELIVERY GUARANTEES
    # ----------------------------------------------------------------
    @staticmethod
    def delivery_guarantees():
        """
        DELIVERY GUARANTEES
        ====================
        Three levels of promise about whether a message reaches the consumer.

        ┌──────────────────┬───────────────────────────────────────────────┐
        │ Guarantee        │ Behaviour                                     │
        ├──────────────────┼───────────────────────────────────────────────┤
        │ At-most-once     │ Sent once; if lost → gone forever.            │
        │ (Fire & Forget)  │ Lowest latency, lowest reliability.           │
        │                  │ Use-case: IoT sensor readings — losing one    │
        │                  │ reading out of 10 000 is acceptable.          │
        ├──────────────────┼───────────────────────────────────────────────┤
        │ At-least-once    │ Retried until ACKed → may be processed TWICE. │
        │                  │ Consumer MUST be idempotent (safe to re-run). │
        │                  │ Use-case: image processing — processing the   │
        │                  │ same image twice just overwrites it. Fine.    │
        │                  │ ← Industry default (RabbitMQ, Redis).        │
        ├──────────────────┼───────────────────────────────────────────────┤
        │ Exactly-once     │ Delivered & processed exactly ONE time.       │
        │ (Holy Grail)     │ Requires transactions across producer,        │
        │                  │ broker, and consumer DB. Complex & slow.      │
        │                  │ Use-case: financial transactions — a credit   │
        │                  │ card must never be charged twice.             │
        │                  │ ← Kafka Streams with transactional IDs.      │
        └──────────────────┴───────────────────────────────────────────────┘

        Key rule: if you use at-least-once, design your consumers to be
        IDEMPOTENT — running them twice must produce the same result.
        """

    # ----------------------------------------------------------------
    # 6.  DEAD LETTER QUEUE (DLQ)
    # ----------------------------------------------------------------
    @staticmethod
    def dead_letter_queue():
        """
        DEAD LETTER QUEUE (DLQ)
        ========================
        A special queue that receives messages which CANNOT be processed
        after a set number of retries, or are structurally invalid.

        Why it exists
        -------------
        Without a DLQ, a "poison pill" message loops forever:
          crash → re-queue → crash → re-queue → … (infinite loop 💀)

        With a DLQ:
          - After N failures the broker PARKS the message in the DLQ.
          - The main queue keeps flowing normally.
          - Engineers inspect the DLQ, fix the root cause, then
            manually REPLAY the messages.

        Real-world example
        ------------------
        Malformed webhook:
          - External API changes its JSON format.
          - Worker throws a parsing error on every attempt.
          - After 3 retries → message moves to DLQ.
          - Alert fires → developer sees the bad payload.
          - Code patched → messages replayed successfully.

        Flow diagram
        ------------
          Producer
              │
              ▼
          [Main Queue]
              │
              ▼
           Consumer ──(fail)──► retry ──(fail)──► retry
                                                     │
                                              (max retries hit)
                                                     │
                                                     ▼
                                              [Dead Letter Queue]
                                                     │
                                                     ▼
                                           Developer Inspection 🔍
        """

    # ----------------------------------------------------------------
    # 7.  BACKPRESSURE
    # ----------------------------------------------------------------
    @staticmethod
    def backpressure():
        """
        BACKPRESSURE
        =============
        A flow-control mechanism that kicks in when the Producer sends
        messages FASTER than the Consumer can process them.

        Without backpressure → queue grows unbounded → OOM crash 💥

        Strategies
        ----------
        1. Block the producer   — broker says "STOP, I'm full."
        2. Drop messages        — shed load by discarding oldest /
                                  least important messages.
        3. Scale consumers      — auto-spin up more worker nodes to
                                  drain the queue faster (Kubernetes
                                  HPA + KEDA are common tools).

        Real-world example
        ------------------
        Flash sale survival:
          - Incoming requests surge to 10 000 req/s.
          - DB can only handle 1 000 writes/s.
          - Queue hits memory limit.
          - Broker rejects new HTTP requests with:
              429 Too Many Requests  OR  503 Service Unavailable
          → Database saved from apocalyptic crash.

        Diagram
        -------
          Producer (1000 msg/s)
               │
               ▼
          [Queue: FULL]  ─── SLOW DOWN! ──► Producer
               │
               ▼
          Consumer (100 msg/s)    ← the bottleneck

          Backpressure bridges the gap between these two speeds.
        """

    # ----------------------------------------------------------------
    # 8.  TOOL SUMMARY — Celery / Redis / RabbitMQ / Kafka
    # ----------------------------------------------------------------
    @staticmethod
    def tools_overview():
        """
        TOOLS AT A GLANCE
        ==================

        ┌─────────────┬──────────────┬───────────────────────────────────┐
        │ Tool        │ Role         │ When to use                       │
        ├─────────────┼──────────────┼───────────────────────────────────┤
        │ Celery      │ Worker       │ Python background tasks.          │
        │             │ framework    │ Sits on top of a broker (Redis or │
        │             │              │ RabbitMQ). Handles task routing,  │
        │             │              │ retries, scheduling (beat),       │
        │             │              │ result backends.                  │
        ├─────────────┼──────────────┼───────────────────────────────────┤
        │ Redis       │ Broker +     │ Fast in-memory store. Low-latency │
        │             │ Cache        │ queues. Not durable by default    │
        │             │              │ (can be configured with AOF/RDB). │
        │             │              │ Great for Celery in small/medium  │
        │             │              │ setups. Redis Streams for more    │
        │             │              │ advanced pub/sub scenarios.       │
        ├─────────────┼──────────────┼───────────────────────────────────┤
        │ RabbitMQ    │ Broker       │ Full AMQP protocol. Supports      │
        │             │              │ complex routing (direct, topic,   │
        │             │              │ fanout, headers exchanges).       │
        │             │              │ Built-in DLQ, TTL, priorities.    │
        │             │              │ Industry standard for task queues.│
        ├─────────────┼──────────────┼───────────────────────────────────┤
        │ Kafka       │ Distributed  │ Massive throughput (millions of   │
        │             │ event log    │ events/sec). Messages stored on   │
        │             │              │ disk and REPLAYABLE. Multiple     │
        │             │              │ consumer groups can read the same │
        │             │              │ log independently. Built-in       │
        │             │              │ exactly-once via transactions.    │
        │             │              │ Use for event sourcing, analytics │
        │             │              │ pipelines, audit logs.            │
        └─────────────┴──────────────┴───────────────────────────────────┘

        Quick decision guide
        --------------------
          Simple Python background jobs?     → Celery + Redis
          Complex routing / reliable tasks?  → Celery + RabbitMQ
          High-throughput event streaming?   → Kafka
          Need replay / audit log?           → Kafka
        """


# ============================================================
# QUICK RECAP PRINTER  (optional — run the file to see it)
# ============================================================

if __name__ == "__main__":
    import inspect

    sections = [
        MessageQueuesNotes.producer_consumer,
        MessageQueuesNotes.message_broker,
        MessageQueuesNotes.queue_vs_pubsub,
        MessageQueuesNotes.acknowledgement,
        MessageQueuesNotes.delivery_guarantees,
        MessageQueuesNotes.dead_letter_queue,
        MessageQueuesNotes.backpressure,
        MessageQueuesNotes.tools_overview,
    ]

    for fn in sections:
        print("=" * 64)
        print(inspect.getdoc(fn))
        print()
