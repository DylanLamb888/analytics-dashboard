"""Database configuration and initialization."""

import duckdb
from pathlib import Path
from core.config import settings


# Global connection
_conn = None


def get_connection():
    """Get database connection."""
    global _conn
    if _conn is None:
        _conn = duckdb.connect(":memory:", read_only=False)
    return _conn


def init_db():
    """Initialize database with tables."""
    conn = get_connection()
    
    # Create orders table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR PRIMARY KEY,
            order_date TIMESTAMP,
            customer_name VARCHAR,
            address_line VARCHAR,
            street VARCHAR,
            city VARCHAR,
            state VARCHAR,
            zip_code VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            item_sku VARCHAR,
            item_name VARCHAR,
            quantity INTEGER,
            unit_price_usd DECIMAL(10, 2),
            order_total DECIMAL(10, 2),
            order_day DATE,
            weekday INTEGER,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON orders(state)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_zip_code ON orders(zip_code)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_item_sku ON orders(item_sku)")
    
    conn.commit()


def clear_orders():
    """Clear all orders from database."""
    conn = get_connection()
    conn.execute("DELETE FROM orders")
    conn.commit()