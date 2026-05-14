import asyncio
import random
import time

async def call_user_service():
    delay = random.randint(1, 3)

    print(f"[User Service] Taking {delay}s")
    await asyncio.sleep(delay)

    return {"user": "Alice"}

async def call_order_service():
    delay = random.randint(1, 3)

    print(f"[Order Service] Taking {delay}s")
    await asyncio.sleep(delay)

    return {"orders": 15}

async def call_billing_service():
    delay = random.randint(1, 3)

    print(f"[Billing Service] Taking {delay}s")
    await asyncio.sleep(delay)

    return {"balance": 250}

async def main():
    print("Starting API Gateway...\n")

    start = time.time()

    user, orders, billing = await asyncio.gather(
        call_user_service(),
        call_order_service(),
        call_billing_service()
    )

    result = {
        **user,
        **orders,
        **billing
    }

    end = time.time()

    print("\nFinal Aggregated Response:")
    print(result)

    print(f"\nTotal Response Time: {end - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
