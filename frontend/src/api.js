export async function fetchLogs(limit = 50) {
  const resp = await fetch(`/api/logs?limit=${limit}`);
  if (!resp.ok) throw new Error("Failed to load logs");
  return resp.json();
}

export async function fetchReviews(limit = 20) {
  const resp = await fetch(`/api/reviews?limit=${limit}`);
  if (!resp.ok) throw new Error("Failed to load reviews");
  return resp.json();
}
