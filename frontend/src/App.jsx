import { useEffect, useState } from "react";
import { fetchLogs, fetchReviews } from "./api.js";

export default function App() {
  const [logs, setLogs] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [logsData, reviewsData] = await Promise.all([
          fetchLogs(),
          fetchReviews(),
        ]);
        if (cancelled) return;
        setLogs(logsData.logs ?? []);
        setReviews(reviewsData.reviews ?? []);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load data");
      }
    }

    load();
    const interval = setInterval(load, 10000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>ReviewFlow</h1>
          <p>Recent logs and review results</p>
        </div>
      </header>

      {error ? <div className="error">{error}</div> : null}

      <section className="panel">
        <h2>Recent Reviews</h2>
        <div className="list">
          {reviews.length === 0 ? (
            <div className="empty">No reviews yet.</div>
          ) : (
            reviews.map((item) => (
              <div className="card" key={item.id}>
                <div className="card-title">
                  {item.owner}/{item.repo} #{item.pr_number}
                </div>
                <div className="card-meta">
                  <span>Phase: {item.phase}</span>
                  <span>SHA: {item.head_sha?.slice(0, 8)}</span>
                  <span>
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
                <pre className="card-body">
                  {JSON.stringify(item.result, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="panel">
        <h2>Task Logs</h2>
        <div className="list">
          {logs.length === 0 ? (
            <div className="empty">No logs yet.</div>
          ) : (
            logs.map((item) => (
              <div className="card" key={item.id}>
                <div className="card-title">{item.event_type}</div>
                <div className="card-meta">
                  <span>Action: {item.action ?? "n/a"}</span>
                  <span>Status: {item.status ?? "n/a"}</span>
                  <span>
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
                <pre className="card-body">
                  {JSON.stringify(item.payload, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
