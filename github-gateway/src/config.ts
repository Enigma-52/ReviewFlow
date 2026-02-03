import dotenv from "dotenv";

dotenv.config();

const requireEnv = (name: string): string => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required env var: ${name}`);
  }
  return value;
};

const parseNumber = (value: string | undefined, fallback: number): number => {
  if (!value) return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const config = {
  port: parseNumber(process.env.PORT, 3000),
  webhookSecret: requireEnv("WEBHOOK_SECRET"),
  db: {
    host: process.env.DB_HOST ?? "localhost",
    port: parseNumber(process.env.DB_PORT, 5432),
    database: process.env.DB_NAME ?? "reviewflow",
    user: process.env.DB_USER ?? "reviewflow",
    password: process.env.DB_PASSWORD ?? "reviewflow",
  },
  redis: {
    url: process.env.REDIS_URL ?? "redis://127.0.0.1:6379",
  },
};
