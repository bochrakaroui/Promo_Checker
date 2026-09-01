"""
PromoChecker API - Database Connection
Handles PostgreSQL connection pool and session management
"""
import os
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Prefer DATABASE_URL (useful for Supabase), fallback to individual DB_* vars.
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DB_CONFIG = {
        'dsn': DATABASE_URL
    }
else:
    DB_CONFIG = {
        'dbname': os.getenv('DB_NAME', 'promochecker'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432))
    }

# Connection pool (min 1, max 10 connections)
try:
    connection_pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        **DB_CONFIG
    )
except Exception as e:
    print(f"❌ Error initializing connection pool: {e}")
    connection_pool = None


def init_connection_pool():
    """Initialize database connection pool"""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **DB_CONFIG
            )
            print("✅ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Error initializing connection pool: {e}")
            raise


def close_connection_pool():
    """Close all connections in the pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("✅ Database connection pool closed")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Automatically returns connection to pool after use
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            connection_pool.putconn(conn)


@contextmanager
def get_db_cursor(dict_cursor=True):
    """
    Context manager for database cursor
    Returns RealDictCursor by default (results as dictionaries)
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            # products = [{'product_key': '...', 'name': '...', ...}, ...]
    """
    with get_db_connection() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


def test_connection():
    """Test database connection"""
    try:
        if connection_pool is None:
            print("❌ Connection pool not initialized")
            return False
            
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM products")
            result = cursor.fetchone()
            print(f"✅ Database connection successful! {result['count']} products found.")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
