import os
import json
import time
import jwt  # pyjwt
import requests
from dotenv import load_dotenv
from redis import Redis
from phase_a import run_phase_a

load_dotenv()

redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")


def load_private_key():
    with open(PRIVATE_KEY_PATH, "r") as f:
        return f.read()


PRIVATE_KEY = load_private_key()


def generate_github_app_jwt():
    now = int(time.time())

    payload = {
        "iat": now - 60,  # issued slightly in past to avoid clock skew
        "exp": now + (10 * 60),  # valid for 10 minutes
        "iss": GITHUB_APP_ID,  # GitHub App ID
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    return token


def get_installation_token(installation_id: int) -> str:
    """
    Exchange App JWT for a short-lived installation access token.
    """
    app_jwt = generate_github_app_jwt()

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.post(url, headers=headers)
    resp.raise_for_status()

    data = resp.json()
    return data["token"]  # valid ~1 hour


def fetch_pr_diff(owner: str, repo: str, pr_id: int, installation_id: int) -> str:
    token = get_installation_token(installation_id)

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    return resp.text  # raw unified diff


def fetch_file_content_from_github(
    owner: str,
    repo: str,
    path: str,
    ref: str,
    installation_token: str,
) -> str:
    """
    Fetch raw file content from GitHub at a specific ref (commit SHA or branch).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"

    headers = {
        "Authorization": f"Bearer {installation_token}",
        "Accept": "application/vnd.github.v3.raw",  # <-- returns plain text
    }

    resp = requests.get(url, headers=headers)

    if resp.status_code == 404:
        raise FileNotFoundError(f"File not found: {path}")

    resp.raise_for_status()
    return resp.text  # raw file content


def process_job(job):
    print("\n=== Processing PR Job ===")
    print(json.dumps(job, indent=2))

    # 1) Fetch diff (unchanged)
    diff = fetch_pr_diff(
        owner=job["owner"],
        repo=job["repo"],
        pr_id=job["prId"],
        installation_id=job["installationId"],
    )

    # 2) Get installation token ONCE per job
    installation_token = get_installation_token(job["installationId"])

    # 3) Real file fetch for Phase A
    def fetch_file_from_github(path: str) -> str:
        return fetch_file_content_from_github(
            owner=job["owner"],
            repo=job["repo"],
            path=path,
            ref=job["headSha"],
            installation_token=installation_token,
        )

    # 4) Run Phase A
    phase_a_output = run_phase_a(diff, fetch_file_from_github)

    print("\n=== Phase A Output ===")

    print("Changed files + hunks:")
    for fd in phase_a_output["file_diffs"]:
        print(f"\nFile: {fd.path}")
        for i, hunk in enumerate(fd.hunks, start=1):
            print(f"  Hunk #{i} (start_line={hunk.start_line})")

            if hunk.added:
                print("    Added lines:")
                for line in hunk.added:
                    print(f"      + {line}")

            if hunk.removed:
                print("    Removed lines:")
                for line in hunk.removed:
                    print(f"      - {line}")

    print("Changed files:")
    for fd in phase_a_output["file_diffs"]:
        print(f" - {fd.path}")

    print("\nSymbols map:")
    print(json.dumps(phase_a_output["symbols_map"], indent=2))

    print("\nRisk summary:")
    print(json.dumps(phase_a_output["risk_summary"], indent=2))
    print("==========================\n")


print("ReviewFlow Python Worker started...")

while True:
    _, job_data = redis_conn.brpop("review-pr-queue")
    job = json.loads(job_data)
    process_job(job)
