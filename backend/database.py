"""Sample analytics warehouse (SQLite) with seed data.

A small e-commerce style schema so IntelliQuery has something realistic to
query out of the box. Everything runs locally with zero external setup.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "warehouse.db"

SCHEMA = """
CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT,
    country       TEXT,
    signup_date   TEXT
);
CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    name          TEXT,
    category      TEXT,
    price         REAL
);
CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER,
    order_date    TEXT,
    status        TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id      INTEGER,
    product_id    INTEGER,
    quantity      INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

SEED = """
INSERT INTO customers VALUES
 (1,'Ava Chen','USA','2025-01-05'),
 (2,'Liam Patel','India','2025-02-11'),
 (3,'Noah Kim','USA','2025-03-02'),
 (4,'Mia Garcia','Canada','2025-03-20'),
 (5,'Ethan Brown','USA','2025-04-15');
INSERT INTO products VALUES
 (1,'Wireless Mouse','Electronics',24.99),
 (2,'Mechanical Keyboard','Electronics',89.00),
 (3,'Standing Desk','Furniture',299.00),
 (4,'Desk Lamp','Furniture',39.50),
 (5,'Noise-Cancel Headphones','Electronics',199.00);
INSERT INTO orders VALUES
 (101,1,'2025-04-01','completed'),
 (102,2,'2025-04-03','completed'),
 (103,1,'2025-05-10','completed'),
 (104,3,'2025-05-12','cancelled'),
 (105,4,'2025-06-01','completed'),
 (106,5,'2025-06-15','completed'),
 (107,2,'2025-06-20','completed');
INSERT INTO order_items VALUES
 (1,101,1,2),(2,101,2,1),(3,102,5,1),(4,103,3,1),
 (5,103,4,2),(6,105,2,1),(7,106,5,2),(8,107,1,3),(9,107,4,1);
"""

def init_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    conn.close()

def run_query(sql: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cols = [d[0] for d in cur.description] if cur.description else []
        return cols, rows
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Warehouse initialized at", DB_PATH)
