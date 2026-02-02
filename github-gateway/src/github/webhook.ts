import { Request, Response } from "express";
import crypto from "crypto";
import { enqueueReviewJob } from "../queue/reviewQueue";
import { pool } from "../db/db";

export function verifyGithubSignature(
  body: string,
  signature: string | undefined,
  secret: string
): boolean {
  if (!signature) return false;

  const hmac = crypto.createHmac("sha256", secret);
  const digest = "sha256=" + hmac.update(body).digest("hex");

  try {
    return crypto.timingSafeEqual(
      Buffer.from(digest),
      Buffer.from(signature)
    );
  } catch {
    return false;
  }
}

export async function githubWebhookHandler(req: Request, res: Response) {
  const signature = req.headers["x-hub-signature-256"] as string | undefined;
  const event = req.headers["x-github-event"] as string | undefined;
  const body = req.body as string;

  const secret = process.env.WEBHOOK_SECRET!;
  if (!verifyGithubSignature(body, signature, secret)) {
    return res.status(401).json({ error: "Invalid signature" });
  }

  if (event === "pull_request") {
    const payload = JSON.parse(body);
    const installationId = payload.installation?.id;

    if (!installationId) {
      console.error("Missing installation_id in webhook");
      return res.status(400).json({ error: "Missing installation_id" });
    }

    // Persist installation mapping (id → owner/repo)
    await pool.query(
      `
      INSERT INTO installations (id, owner, repo)
      VALUES ($1, $2, $3)
      ON CONFLICT (id) DO NOTHING
      `,
      [
        installationId,
        payload.repository.owner.login,
        payload.repository.name,
      ]
    );

    if (
      payload.action === "opened" ||
      payload.action === "synchronize"
    ) {
      const job = {
        prId: payload.pull_request.number,
        repo: payload.repository.name,
        owner: payload.repository.owner.login,
        installationId,              // <-- NEW
        baseSha: payload.pull_request.base.sha,
        headSha: payload.pull_request.head.sha,
        action: payload.action,
      };

      await enqueueReviewJob(job);
      console.log("Enqueued PR Job:", job);

      return res.json({ received: true });
    }
  }

  return res.json({ ignored: true });
}
