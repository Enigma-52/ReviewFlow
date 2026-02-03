import { createApp } from "./app";
import { githubWebhookHandler } from "./github/webhook";
import express from "express";
import { initDb } from "./db/db";
import { config } from "./config";

const app = createApp();

// IMPORTANT: GitHub needs the raw body for signature verification
app.use(
  "/github/webhook",
  express.raw({ type: "application/json" }),
  githubWebhookHandler
);

(async () => {
  try {
    await initDb(); // <-- moved inside async block
    app.listen(config.port, () => {
      console.log(`ReviewFlow Gateway running on port ${config.port}`);
    });
  } catch (err) {
    console.error("Failed to initialize DB:", err);
    process.exit(1);
  }
})();
