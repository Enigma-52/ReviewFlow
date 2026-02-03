import { Pool } from "pg";
import { config } from "../config";

export const pool = new Pool(config.db);

export async function initDb() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS installations (
      id BIGINT PRIMARY KEY,
      owner TEXT NOT NULL,
      repo TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `);
}
