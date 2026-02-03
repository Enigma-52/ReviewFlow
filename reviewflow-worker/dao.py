from typing import Optional
from psycopg2.extras import Json
from db_pool import get_conn, put_conn

SQL = {
    "upsert_review_result": """
        INSERT INTO review_results (
          task_id,
          owner,
          repo,
          pr_number,
          head_sha,
          phase,
          result
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (owner, repo, pr_number, head_sha, phase)
        DO UPDATE SET
          result = EXCLUDED.result,
          created_at = NOW()
    """,
    "insert_task_log": """
        INSERT INTO review_task_logs (
          task_id,
          event_type,
          action,
          status,
          payload
        )
        VALUES (%s, %s, %s, %s, %s)
    """,
    "update_task_status": """
        UPDATE review_tasks
        SET status = %s
        WHERE id = %s
    """,
}


def upsert_review_result(
    task_id: Optional[int],
    owner: str,
    repo: str,
    pr_number: int,
    head_sha: str,
    phase: str,
    result: dict,
) -> None:
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL["upsert_review_result"],
                    (
                        task_id,
                        owner,
                        repo,
                        pr_number,
                        head_sha,
                        phase,
                        Json(result),
                    ),
                )
    finally:
        put_conn(conn)


def append_task_log(
    task_id: Optional[int],
    event_type: str,
    action: Optional[str],
    status: Optional[str],
    payload: dict,
) -> None:
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL["insert_task_log"],
                    (
                        task_id,
                        event_type,
                        action,
                        status,
                        Json(payload),
                    ),
                )
    finally:
        put_conn(conn)


def update_task_status(task_id: Optional[int], status: str) -> None:
    if task_id is None:
        return
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL["update_task_status"], (status, task_id))
    finally:
        put_conn(conn)
