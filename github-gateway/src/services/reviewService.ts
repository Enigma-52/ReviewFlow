import { listRecentReviews } from "../db/dao";

export async function getRecentReviews(limit: number) {
  return listRecentReviews(limit);
}
