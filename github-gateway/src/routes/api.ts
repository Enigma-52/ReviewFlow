import { Router } from "express";
import { asyncHandler } from "../middleware/asyncHandler";
import { getRecentLogs } from "../services/logService";
import { getRecentReviews } from "../services/reviewService";

export const apiRouter = Router();

const parseLimit = (value: unknown, fallback: number) => {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback;
  return Math.min(parsed, 200);
};

apiRouter.get(
  "/logs",
  asyncHandler(async (req, res) => {
    const limit = parseLimit(req.query.limit, 50);
    const logs = await getRecentLogs(limit);
    res.json({ logs });
  })
);

apiRouter.get(
  "/reviews",
  asyncHandler(async (req, res) => {
    const limit = parseLimit(req.query.limit, 20);
    const reviews = await getRecentReviews(limit);
    res.json({ reviews });
  })
);
