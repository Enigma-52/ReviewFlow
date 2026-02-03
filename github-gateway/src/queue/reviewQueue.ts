import { Redis } from "ioredis";
import { config } from "../config";

export const redis = new Redis(config.redis.url);

export async function enqueueReviewJob(job: any) {
  await redis.rpush("review-pr-queue", JSON.stringify(job));
}
