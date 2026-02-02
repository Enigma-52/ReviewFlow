import os
import json
import time
from dotenv import load_dotenv
from redis import Redis

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)


def process_job(job_payload):
    print("=== Received Review Job ===")
    print(json.dumps(job_payload, indent=2))
    print("==========================")


print("ReviewFlow Python Worker started...")

while True:
    # BRPOP = blocking pop (waits if queue is empty)
    _, job_data = redis_conn.brpop("review-pr-queue")
    job = json.loads(job_data)
    process_job(job)
