import { Request, Response } from "express";
import crypto from "crypto";
import { enqueueReviewJob } from "../queue/reviewQueue";
import { config } from "../config";
import { handlePullRequestEvent } from "../services/webhookService";

export function verifyGithubSignature(
  body: Buffer,
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
  const deliveryId = req.headers["x-github-delivery"] as string | undefined;
  const body = req.body as Buffer;

  if (!event) {
    return res.status(400).json({ error: "Missing X-GitHub-Event header" });
  }

  const secret = config.webhookSecret;
  if (!verifyGithubSignature(body, signature, secret)) {
    return res.status(401).json({ error: "Invalid signature" });
  }

  if (event === "ping") {
    return res.json({ ok: true });
  }

  if (event !== "pull_request") {
    return res.status(202).json({ ignored: true });
  }

  const payload = JSON.parse(body.toString("utf8"));

  try {
    const result = await handlePullRequestEvent({
      payload,
      eventType: event,
      deliveryId,
    });

    if (result.status === "ignored") {
      return res.status(202).json({ ignored: true });
    }

    if (result.status === "closed") {
      return res.json({ received: true, status: "closed" });
    }

    if (result.job) {
      await enqueueReviewJob(result.job);
      console.log("Enqueued PR Job:", result.job);
    }

    return res.json({ received: true });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Failed to process webhook";
    return res.status(400).json({ error: message });
  }
}
