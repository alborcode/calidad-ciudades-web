# SQLite Reference

SQLite = base de datos SQL embebida en archivo único. Sin servidor.

## QUICK START

```sql
-- Create table
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);

-- Insert
INSERT INTO users (name) VALUES ('Juan');

-- Select
SELECT * FROM users WHERE id = 1;

-- Update
UPDATE users SET name = 'Juan Updated' WHERE id = 1;

-- Delete
DELETE FROM users WHERE id = 1;
```

---

## CREATE TABLE

```sql
CREATE TABLE tabla (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- auto ID
    nombre TEXT NOT NULL,                  -- required
    email TEXT UNIQUE,                    -- no duplicates
    edad INTEGER DEFAULT 18,              -- default value
    fecha TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## TYPES

| Declare | Stores |
|---------|-------|
| INTEGER | 1, 2, 3 |
| REAL | 1.5, 3.14 |
| TEXT | "string" |
| BLOB | binary |

SQLite uses dynamic typing - can store any type in any column.

## SELECT

```sql
-- Basic
SELECT * FROM tabla;
SELECT col1, col2 FROM tabla WHERE id = 1;

-- Order/Limit
SELECT * FROM tabla ORDER BY id DESC LIMIT 10;

-- Join
SELECT u.name, p.title 
FROM users u 
JOIN posts p ON u.id = p.user_id;

-- Group
SELECT dept, COUNT(*) FROM emp GROUP BY dept HAVING COUNT(*) > 2;
```

## INSERT/UPDATE

```sql
-- Insert
INSERT INTO tabla (col) VALUES ('val');

-- Upsert (insert or update)
INSERT INTO users (id, name) VALUES (1, 'Juan')
ON CONFLICT(id) DO UPDATE SET name = 'New Juan';

-- Update
UPDATE users SET name = 'Juan' WHERE id = 1;
```

## INDEXES

```sql
CREATE INDEX idx_col ON tabla(col);
CREATE INDEX idx_2col ON tabla(col1, col2);
```

## TRANSACTIONS

```sql
BEGIN TRANSACTION;
UPDATE ...;
UPDATE ...;
COMMIT;  -- or ROLLBACK;
```

## FUNCTIONS

```sql
-- String: UPPER, LOWER, LENGTH, SUBSTR, REPLACE
-- Math: ABS, ROUND, RANDOM
-- Date: DATE('now'), DATE('now', '+1 day')
-- Null: COALESCE(col, 'default')
-- Aggregate: COUNT, SUM, AVG, MIN, MAX
```

## CLI

```bash
sqlite3 mydb.db
.tables          -- list tables
.schema          -- show tables
.quit
```

## REFERENCE

./references/documentation.md - Full reference