import json
from phase_a import run_phase_a
from github_client import GitHubAppClient
from dao import append_task_log, upsert_review_result, update_task_status


def process_job(job: dict, client: GitHubAppClient) -> None:
    print("\n=== Processing PR Job ===")
    print(json.dumps(job, indent=2))

    diff = client.fetch_pr_diff(
        owner=job["owner"],
        repo=job["repo"],
        pr_id=job["prId"],
        installation_id=job["installationId"],
    )

    installation_token = client.get_installation_token(job["installationId"])

    def fetch_file_from_github(path: str) -> str:
        return client.fetch_file_content(
            owner=job["owner"],
            repo=job["repo"],
            path=path,
            ref=job["headSha"],
            installation_token=installation_token,
        )

    phase_a_output = run_phase_a(diff, fetch_file_from_github)

    result_payload = {
        "file_diffs": [
            {
                "path": fd.path,
                "hunks": [
                    {
                        "start_line": hunk.start_line,
                        "added": hunk.added,
                        "removed": hunk.removed,
                    }
                    for hunk in fd.hunks
                ],
            }
            for fd in phase_a_output["file_diffs"]
        ],
        "symbols_map": phase_a_output["symbols_map"],
        "risk_summary": phase_a_output["risk_summary"],
    }

    upsert_review_result(
        task_id=job.get("taskId"),
        owner=job["owner"],
        repo=job["repo"],
        pr_number=job["prId"],
        head_sha=job["headSha"],
        phase="phase_a",
        result=result_payload,
    )

    update_task_status(job.get("taskId"), "completed")

    append_task_log(
        task_id=job.get("taskId"),
        event_type="analysis_completed",
        action=job.get("action"),
        status="completed",
        payload={
            "owner": job["owner"],
            "repo": job["repo"],
            "pr_number": job["prId"],
            "head_sha": job["headSha"],
            "phase": "phase_a",
        },
    )

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
