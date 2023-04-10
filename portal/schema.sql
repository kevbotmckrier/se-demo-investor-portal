DROP TABLE IF EXISTS company_bank_accounts;
DROP TABLE IF EXISTS company_ledger_accounts;
DROP TABLE IF EXISTS company_ledger_account_categories;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_ledger_accounts;
DROP TABLE IF EXISTS user_ledger_account_categories;

CREATE TABLE company_account_categories_with_bank_accounts (
  account_category_name TEXT PRIMARY KEY,
  bank TEXT,
  vendor TEXT,
  internal_account_id TEXT,
  external_account_id TEXT,
  internal_account_name TEXT,
  internal_account_party_name TEXT,
  connection_id TEXT,
  currency TEXT,
  bank_name TEXT NOT NULL,
  currency TEXT NOT NULL,
  metadata BLOB
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  attributes BLOB
);

