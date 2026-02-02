import { Redis } from "ioredis";

export const redis = new Redis({
  host: "127.0.0.1",
  port: 6379,
});

export async function enqueueReviewJob(job: any) {
  await redis.rpush("review-pr-queue", JSON.stringify(job));
}
