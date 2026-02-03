import { pool } from "./pool";

const SQL = {
  createInstallationsTable: `
    CREATE TABLE IF NOT EXISTS installations (
      id BIGINT PRIMARY KEY,
      owner TEXT NOT NULL,
      repo TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `,
  createReviewTasksTable: `
    CREATE TABLE IF NOT EXISTS review_tasks (
      id BIGSERIAL PRIMARY KEY,
      installation_id BIGINT NOT NULL,
      owner TEXT NOT NULL,
      repo TEXT NOT NULL,
      pr_number INTEGER NOT NULL,
      base_sha TEXT,
      head_sha TEXT NOT NULL,
      action TEXT NOT NULL,
      event_type TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'queued',
      queued_at TIMESTAMP DEFAULT NOW(),
      metadata JSONB
    );
  `,
  createReviewTasksIndex: `
    CREATE UNIQUE INDEX IF NOT EXISTS review_tasks_unique_key
    ON review_tasks (installation_id, owner, repo, pr_number, head_sha);
  `,
  createReviewTaskLogsTable: `
    CREATE TABLE IF NOT EXISTS review_task_logs (
      id BIGSERIAL PRIMARY KEY,
      task_id BIGINT REFERENCES review_tasks(id),
      event_type TEXT NOT NULL,
      action TEXT,
      status TEXT,
      payload JSONB,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `,
  createReviewResultsTable: `
    CREATE TABLE IF NOT EXISTS review_results (
      id BIGSERIAL PRIMARY KEY,
      task_id BIGINT REFERENCES review_tasks(id),
      owner TEXT NOT NULL,
      repo TEXT NOT NULL,
      pr_number INTEGER NOT NULL,
      head_sha TEXT NOT NULL,
      phase TEXT NOT NULL,
      result JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `,
  createReviewResultsIndex: `
    CREATE UNIQUE INDEX IF NOT EXISTS review_results_unique_key
    ON review_results (owner, repo, pr_number, head_sha, phase);
  `,
  upsertInstallation: `
    INSERT INTO installations (id, owner, repo)
    VALUES ($1, $2, $3)
    ON CONFLICT (id) DO NOTHING
  `,
  upsertReviewTask: `
    INSERT INTO review_tasks (
      installation_id,
      owner,
      repo,
      pr_number,
      base_sha,
      head_sha,
      action,
      event_type,
      status,
      metadata
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    ON CONFLICT (installation_id, owner, repo, pr_number, head_sha)
    DO UPDATE SET
      base_sha = EXCLUDED.base_sha,
      action = EXCLUDED.action,
      event_type = EXCLUDED.event_type,
      status = EXCLUDED.status,
      queued_at = NOW(),
      metadata = EXCLUDED.metadata
    RETURNING id
  `,
  insertTaskLog: `
    INSERT INTO review_task_logs (task_id, event_type, action, status, payload)
    VALUES ($1, $2, $3, $4, $5)
  `,
  listTaskLogs: `
    SELECT id, task_id, event_type, action, status, payload, created_at
    FROM review_task_logs
    ORDER BY created_at DESC
    LIMIT $1
  `,
  listRecentReviews: `
    SELECT
      id,
      task_id,
      owner,
      repo,
      pr_number,
      head_sha,
      phase,
      result,
      created_at
    FROM review_results
    ORDER BY created_at DESC
    LIMIT $1
  `,
};

export async function initDb() {
  await pool.query(SQL.createInstallationsTable);
  await pool.query(SQL.createReviewTasksTable);
  await pool.query(SQL.createReviewTasksIndex);
  await pool.query(SQL.createReviewTaskLogsTable);
  await pool.query(SQL.createReviewResultsTable);
  await pool.query(SQL.createReviewResultsIndex);
}

export async function upsertInstallation(
  installationId: number,
  owner: string,
  repo: string
) {
  await pool.query(SQL.upsertInstallation, [installationId, owner, repo]);
}

export async function upsertReviewTask(params: {
  installationId: number;
  owner: string;
  repo: string;
  prNumber: number;
  baseSha: string;
  headSha: string;
  action: string;
  eventType: string;
  status: string;
  metadata: Record<string, unknown>;
}) {
  const result = await pool.query(SQL.upsertReviewTask, [
    params.installationId,
    params.owner,
    params.repo,
    params.prNumber,
    params.baseSha,
    params.headSha,
    params.action,
    params.eventType,
    params.status,
    params.metadata,
  ]);
  return result.rows[0]?.id as number | undefined;
}

export async function insertTaskLog(params: {
  taskId?: number;
  eventType: string;
  action?: string;
  status?: string;
  payload: Record<string, unknown>;
}) {
  await pool.query(SQL.insertTaskLog, [
    params.taskId ?? null,
    params.eventType,
    params.action ?? null,
    params.status ?? null,
    params.payload,
  ]);
}

export async function listTaskLogs(limit: number) {
  const result = await pool.query(SQL.listTaskLogs, [limit]);
  return result.rows;
}

export async function listRecentReviews(limit: number) {
  const result = await pool.query(SQL.listRecentReviews, [limit]);
  return result.rows;
}
