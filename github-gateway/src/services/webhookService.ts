import { insertTaskLog, upsertInstallation, upsertReviewTask } from "../db/dao";

type PullRequestPayload = {
  action?: string;
  installation?: { id?: number };
  repository: {
    name: string;
    owner: { login: string };
  };
  pull_request: {
    number: number;
    base: { sha: string };
    head: { sha: string };
  };
  sender?: { login?: string };
};

export type WebhookJob = {
  taskId?: number;
  prId: number;
  repo: string;
  owner: string;
  installationId: number;
  baseSha: string;
  headSha: string;
  action: string;
};

export async function handlePullRequestEvent(params: {
  payload: PullRequestPayload;
  eventType: string;
  deliveryId?: string;
}): Promise<{ status: "ignored" | "closed" | "queued"; job?: WebhookJob }> {
  const { payload, eventType, deliveryId } = params;
  const installationId = payload.installation?.id;
  if (!installationId) {
    throw new Error("Missing installation_id");
  }

  const action = payload.action;
  const allowedActions = new Set([
    "opened",
    "synchronize",
    "reopened",
    "closed",
  ]);

  if (!action || !allowedActions.has(action)) {
    return { status: "ignored" };
  }

  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;
  const prNumber = payload.pull_request.number;
  const baseSha = payload.pull_request.base.sha;
  const headSha = payload.pull_request.head.sha;
  const status = action === "closed" ? "closed" : "queued";

  await upsertInstallation(installationId, owner, repo);

  const taskId = await upsertReviewTask({
    installationId,
    owner,
    repo,
    prNumber,
    baseSha,
    headSha,
    action,
    eventType,
    status,
    metadata: {
      deliveryId,
      sender: payload.sender?.login,
    },
  });

  await insertTaskLog({
    taskId,
    eventType,
    action,
    status,
    payload: {
      deliveryId,
      sender: payload.sender?.login,
      owner,
      repo,
      prNumber,
      baseSha,
      headSha,
    },
  });

  if (action === "closed") {
    return { status: "closed" };
  }

  return {
    status: "queued",
    job: {
      taskId,
      prId: prNumber,
      repo,
      owner,
      installationId,
      baseSha,
      headSha,
      action,
    },
  };
}
