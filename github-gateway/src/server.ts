import { createApp } from "./app";
import { githubWebhookHandler } from "./github/webhook";
import express from "express";
import dotenv from "dotenv";

dotenv.config();

const app = createApp();

// IMPORTANT: GitHub needs the raw body for signature verification
app.use(
  "/github/webhook",
  express.raw({ type: "application/json" }),
  githubWebhookHandler
);

const PORT = Number(process.env.PORT) || 3000;

app.listen(PORT, () => {
  console.log(`ReviewFlow Gateway running on port ${PORT}`);
});
