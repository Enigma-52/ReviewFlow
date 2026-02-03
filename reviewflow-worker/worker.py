import json
from redis import Redis
from config import settings
from github_client import GitHubAppClient, load_private_key
from processor import process_job


def main() -> None:
    redis_conn = Redis.from_url(settings.redis_url)
    private_key = load_private_key(settings.github_private_key_path)
    client = GitHubAppClient(settings=settings, private_key=private_key)

    print("ReviewFlow Python Worker started...")

    while True:
        _, job_data = redis_conn.brpop("review-pr-queue")
        job = json.loads(job_data)
        process_job(job, client)


if __name__ == "__main__":
    main()
