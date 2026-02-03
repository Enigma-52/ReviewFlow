# ReviewFlow

ReviewFlow is split into two small services:
1. `github-gateway`: Express webhook receiver that validates GitHub signatures, stores installation mappings, and enqueues PR review jobs in Redis.
2. `reviewflow-worker`: Python worker that pulls jobs from Redis, fetches diffs/files from GitHub using the App installation token, and runs Phase A analysis.

## Repo Layout (Short)
1. `github-gateway/src/server.ts`: app bootstrap and DB init.
2. `github-gateway/src/github/webhook.ts`: webhook handler and job enqueueing.
3. `github-gateway/src/db/dao.ts`: Postgres DAO + schema init.
4. `github-gateway/src/queue/reviewQueue.ts`: Redis queue client.
5. `reviewflow-worker/worker.py`: worker entrypoint and job loop.
6. `reviewflow-worker/processor.py`: PR job processing pipeline.
7. `reviewflow-worker/github_client.py`: GitHub App auth + API calls.
8. `frontend/`: simple React UI for logs and recent reviews.

## Environment Files
1. `github-gateway/.env.example`
2. `reviewflow-worker/.env.example`

Copy them to `.env` in each service and fill in real values.
