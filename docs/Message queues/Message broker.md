# Message Broker

> [!NOTE]  
> A Message Broker is an intermediary server that routes, stores, and delivers messages between producers and consumers. It acts as the post office of a distributed system. 

## Concept Explanation

Brokers handle the complex networking, persistence, and routing rules required to ensure that a message produced by one application is reliably delivered to one or many consuming applications, even if they are written in different languages or reside on different servers.

## Distributed Systems Use Case

> [!TIP]
> **Service Decoupling & Resilience**  
> Microservices communicate through the broker. If the "Payment Service" goes down, the "Order Service" can still accept orders and send messages to the broker. The broker stores these messages safely on disk. Once the Payment Service comes back online, it reads the backlog of messages from the broker and processes them, preventing data loss.

## Routing Diagram

```mermaid
graph TD
    A[Service A (Producer)] -->|Send| B((Message Broker))
    C[Service C (Producer)] -->|Send| B
    B -->|Route & Deliver| D[Service D (Consumer)]
    B -->|Route & Deliver| E[Service E (Consumer)]
```
