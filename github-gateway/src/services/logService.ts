import { listTaskLogs } from "../db/dao";

export async function getRecentLogs(limit: number) {
  return listTaskLogs(limit);
}
