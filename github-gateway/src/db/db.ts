import { Pool } from "pg";

export const pool = new Pool({
  host: "localhost",
  port: 5432,
  database: "reviewflow",
  user: "reviewflow",
  password: "reviewflow",
});

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
