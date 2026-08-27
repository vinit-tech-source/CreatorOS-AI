import sqlite3 from 'sqlite3';
import path from 'path';
import fs from 'fs';

// Ensure the data directory exists
const dataDir = path.join(__dirname, '../../data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

export const db = new sqlite3.Database(path.join(dataDir, 'database.sqlite'));

export function initDb() {
  return new Promise<void>((resolve, reject) => {
    db.serialize(() => {
      // Table: connected_accounts
      db.run(`
        CREATE TABLE IF NOT EXISTS connected_accounts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          platform TEXT NOT NULL DEFAULT 'twitter',
          access_token TEXT NOT NULL,
          refresh_token TEXT,
          token_expires_at DATETIME,
          twitter_user_id TEXT,
          twitter_username TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Table: posts
      db.run(`
        CREATE TABLE IF NOT EXISTS posts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          connected_account_id INTEGER NOT NULL,
          content_text TEXT NOT NULL,
          media_url TEXT,
          status TEXT NOT NULL DEFAULT 'pending',
          platform_post_id TEXT,
          platform_post_url TEXT,
          error_message TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (connected_account_id) REFERENCES connected_accounts (id)
        )
      `, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  });
}

// Simple wrapper for async queries
export function dbGet<T>(sql: string, params: any[] = []): Promise<T | undefined> {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row as T);
    });
  });
}

export function dbRun(sql: string, params: any[] = []): Promise<number> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}

export function dbAll<T>(sql: string, params: any[] = []): Promise<T[]> {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows as T[]);
    });
  });
}
