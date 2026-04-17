# SQLite Reference

## CREATE TABLE

```sql
-- Basic
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);

-- With constraints
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    edad INTEGER DEFAULT 18,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Without ROWID (fast write)
CREATE TABLE logs (id INTEGER PRIMARY KEY, msg TEXT) WITHOUT ROWID;

-- STRICT (type enforcement)
CREATE TABLE t (id INTEGER, name TEXT) STRICT;
```

## SELECT

```sql
-- Basic
SELECT * FROM tabla;
SELECT col1, col2 FROM tabla WHERE id = 1;

-- Joins
SELECT u.name, p.title FROM users u 
JOIN posts p ON u.id = p.user_id;

SELECT u.name, p.title FROM users u 
LEFT JOIN posts p ON u.id = p.user_id;

-- WHERE modifiers
WHERE name LIKE '%juan%';
WHERE id IN (1, 2, 3);
WHERE edad BETWEEN 18 AND 65;

-- Aggregation
SELECT dept, COUNT(*), AVG(salary), SUM(bonus)
FROM employees 
GROUP BY dept 
HAVING COUNT(*) > 2;

-- Subqueries
SELECT * FROM t WHERE col > (SELECT AVG(col) FROM t);

-- Common patterns
SELECT DISTINCT col FROM tabla;
SELECT col1 + col2 AS total FROM t;
SELECT * FROM t ORDER BY col DESC LIMIT 10;
SELECT * FROM t LIMIT 10 OFFSET 20;
```

## INSERT/UPDATE/DELETE

```sql
-- Insert
INSERT INTO users (name) VALUES ('Juan');
INSERT INTO users (name, email) SELECT name, email FROM old_users;

-- Insert multiple
INSERT INTO users (name) VALUES ('A'), ('B'), ('C');

-- Update
UPDATE users SET name = 'Juan' WHERE id = 1;
UPDATE users SET col1 = x + 1 WHERE id = 1;

-- Delete
DELETE FROM users WHERE id = 1;
DELETE FROM users;  -- all rows

-- Upsert
INSERT INTO users (id, name) VALUES (1, 'Juan')
ON CONFLICT(id) DO UPDATE SET name = 'New Juan';
```

## INDEXES

```sql
-- Basic
CREATE INDEX idx_name ON users(name);

-- Composite
CREATE INDEX idx_a_b ON tabla(col_a, col_b);

-- Unique
CREATE UNIQUE INDEX idx_email ON users(email);

-- Partial
CREATE INDEX idx_active ON users(status) WHERE status = 1;
```

## TRANSACTIONS

```sql
BEGIN TRANSACTION;
UPDATE cuentas SET saldo = saldo - 100 WHERE id = 1;
UPDATE cuentas SET saldo = saldo + 100 WHERE id = 2;
COMMIT;  -- or ROLLBACK;
```

## CONSTRAINTS

```sql
-- NOT NULL
name TEXT NOT NULL

-- UNIQUE
email TEXT UNIQUE

-- CHECK
edad INTEGER CHECK(edad >= 0)

-- DEFAULT
estado TEXT DEFAULT 'active'

-- PRIMARY KEY
id INTEGER PRIMARY KEY

-- FOREIGN KEY
usuario_id INTEGER REFERENCES usuarios(id)
```

## FUNCTIONS

```sql
-- String
UPPER/LOWER, LENGTH, SUBSTR, REPLACE, TRIM, INSTR, GROUP_CONCAT

-- Math  
ABS, ROUND, RANDOM, POWER, MOD, CEIL, FLOOR

-- Date
DATE('now'), TIME('now'), DATETIME('now')
DATE('now', '+1 day'), DATE('now', '-1 month')

-- Null
COALESCE(col, 'default'), IFNULL(col, 'default'), NULLIF(a,b)

-- Type
TYPEOF(col), CAST(val AS INTEGER)

-- Aggregate
COUNT, SUM, AVG, MIN, MAX, TOTAL
```

## PRAGMAS

```sql
PRAGMA table_info(tabla);     -- estructura
PRAGMA index_list(tabla);    -- índices
PRAGMA database_list;       -- dbs
PRAGMA journal_mode = WAL;  -- WAL mode
PRAGMA synchronous = NORMAL;
```

## CLI COMMANDS

```bash
sqlite3 database.db

.tables           -- list tables
.schema          -- show create statements
.indexes         -- list indexes
.mode column    -- format output
.headers on     -- show column headers
.explain query plan SELECT ...  -- show query plan
.quit
```

## COMMON ERRORS

| Error | Fix |
|-------|-----|
| UNIQUE constraint | Remove UNIQUE or use different value |
| NOT NULL constraint | Provide value or use DEFAULT |
| CHECK constraint failed | Value violates CHECK expression |
| database locked | Use transaction, COMMIT, or WAL mode |
| no such table | Check table name or run CREATE TABLE |

## EXAMPLE FULL WORKFLOW

```sql
-- Create
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL DEFAULT 0,
    stock INTEGER DEFAULT 0
);

-- Index
CREATE INDEX idx_price ON products(price);

-- Insert
INSERT INTO products (name, price, stock) VALUES 
('Widget', 9.99, 100),
('Gadget', 19.99, 50);

-- Query
SELECT name, price FROM products WHERE stock > 0 ORDER BY price;

-- Update stock
UPDATE products SET stock = stock - 1 WHERE id = 1;

-- Report
SELECT COUNT(*) total, SUM(stock) inventario FROM products;
```

## RESOURCES

- Doc: https://sqlite.org/lang.html
- Try online: https://sqlite.org/fiddle