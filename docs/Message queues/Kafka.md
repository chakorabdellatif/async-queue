# Kafka Architecture

## Concept Explanation
Apache Kafka is fundamentally different from traditional message brokers like RabbitMQ. It is a **Distributed Event Streaming Platform**. Instead of a queue where messages are deleted after being read, Kafka is an **Append-Only Log**.

Messages (Events) are appended to a "Topic". Consumers read the log sequentially using an "Offset" (a pointer to their current location). Because messages are not deleted upon consumption, multiple different consumer groups can read the same stream of events at their own pace, and you can even "rewind" time to re-process past events.

## Architecture & Components
1. **Topic:** A category or feed name (the Log).
2. **Partitions:** Topics are split into partitions across multiple servers for massive parallel scalability.
3. **Producer:** Appends events to the end of a partition.
4. **Consumer Group:** A group of workers. Kafka ensures that each partition is read by exactly one consumer within a group.
5. **Offset:** An integer tracking how far a consumer has read into a partition.

## Diagram
```mermaid
graph LR
    P[Producer] -->|Append| T[Topic Partition 0]
    P -->|Append| T2[Topic Partition 1]
    
    subgraph Kafka Cluster (Append-Only Logs)
        T[Event 0 | Event 1 | Event 2 | Event 3]
        T2[Event 0 | Event 1 | Event 2]
    end
    
    T -->|Offset=2| C1[Consumer A (Group 1)]
    T2 -->|Offset=1| C2[Consumer B (Group 1)]
```
