import random
import asyncio
import os
from datetime import datetime, timedelta, timezone
from faker import Faker
import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/")
API_KEY = os.getenv("API_KEY", "vlab-secret-key-2024")

fake = Faker("pt_BR")

FUEL_PRICES = {
    "GASOLINA": (5.0, 6.2),
    "ETANOL": (3.2, 4.2),
    "DIESEL": (5.8, 6.8),
}


def random_timestamp():
    now = datetime.now(timezone.utc)
    days_ago = random.randint(0, 30)
    return (now - timedelta(days=days_ago)).isoformat()


def generate_refueling():
    fuel = random.choice(list(FUEL_PRICES.keys()))
    price_min, price_max = FUEL_PRICES[fuel]

    return {
        "station_id": random.randint(1, 50),
        "timestamp": random_timestamp(),
        "fuel_type": fuel,
        "price_per_liter": str(round(random.uniform(price_min, price_max), 2)),
        "volume_liters": str(round(random.uniform(10, 80), 2)),
        "driver_cpf": fake.cpf().replace(".", "").replace("-", "")
    }


async def send_requests(total: int = 100):
    headers = {"X-API-Key": API_KEY}
    successful = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(total):
            payload = generate_refueling()
            try:
                response = await client.post(API_URL, json=payload, headers=headers)
                if response.status_code == 201:
                    successful += 1
                    if (i + 1) % 10 == 0:
                        print(f"Progress: {i + 1}/{total}")
                else:
                    failed += 1
                    print(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                failed += 1
                print(f"Exception: {e}")
    
    print(f"\nCompleted: {successful} successful, {failed} failed")


if __name__ == "__main__":
    asyncio.run(send_requests(200))
