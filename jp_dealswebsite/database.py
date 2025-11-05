"""
Database connection module for Supabase PostgreSQL
"""
import os

# Try to import psycopg2, but handle gracefully if it fails
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError as e:
    PSYCOPG2_AVAILABLE = False
    PSYCOPG2_ERROR = str(e)
    print(f"Warning: psycopg2 not available: {e}")
    # Create stub classes to prevent crashes
    class psycopg2:
        class pool:
            @staticmethod
            def SimpleConnectionPool(*args, **kwargs):
                raise Exception(f"psycopg2 not available: {PSYCOPG2_ERROR}")
        class extras:
            class RealDictCursor:
                pass

# Database connection pool
_connection_pool = None

def get_db_connection():
    """Get a database connection from the pool"""
    global _connection_pool
    
    if not PSYCOPG2_AVAILABLE:
        raise Exception(f"psycopg2 not available: {PSYCOPG2_ERROR}. Make sure psycopg2-binary is installed.")
    
    # Get Supabase connection string from environment
    # Check DATABASE_URL1 first, then fall back to DATABASE_URL
    database_url = os.environ.get('DATABASE_URL1') or os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise Exception(
            "DATABASE_URL or DATABASE_URL1 environment variable is not set. "
            "Please set it in Vercel Dashboard → Settings → Environment Variables. "
            "Get your connection string from Supabase Dashboard → Settings → Database → Connection string (URI). "
            "⚠️ IMPORTANT: Use 'Session mode' or 'Transaction mode' (not Direct connection) for IPv4 compatibility!"
        )
    
    # Create connection pool if it doesn't exist
    if _connection_pool is None:
        try:
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,  # min connections
                10,  # max connections
                database_url
            )
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error message for IPv4 issues
            if 'could not translate host name' in error_msg.lower() or 'name resolution' in error_msg.lower():
                raise Exception(
                    f"Connection failed: {error_msg}. "
                    "⚠️ This usually means you're using 'Direct connection' which is IPv6-only. "
                    "Use 'Session mode' or 'Transaction mode' connection string from Supabase instead!"
                )
            raise Exception(f"Failed to connect to database: {str(e)}. Please check your DATABASE_URL.")
    
    try:
        return _connection_pool.getconn()
    except Exception as e:
        raise Exception(f"Failed to get database connection: {str(e)}")

def return_db_connection(conn):
    """Return a connection to the pool"""
    global _connection_pool
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn)
        except Exception as e:
            print(f"Warning: Error returning connection to pool: {e}")

def get_db():
    """Get a database cursor with dict-like rows"""
    conn = get_db_connection()
    conn.autocommit = False
    return conn, conn.cursor(cursor_factory=RealDictCursor)

def init_db():
    """Initialize database tables"""
    conn, cur = get_db()
    
    try:
        # Create categories table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create deals table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                price REAL NOT NULL,
                original_price REAL,
                discount INTEGER,
                image_filename TEXT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                description TEXT,
                stock_quantity INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create deal_of_the_day table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS deal_of_the_day (
                id SERIAL PRIMARY KEY,
                deal_id INTEGER NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Check if default categories exist
        cur.execute("SELECT COUNT(*) FROM categories")
        count = cur.fetchone()['count']
        
        if count == 0:
            # Insert default categories
            default_categories = [
                ('Electronics', 'electronics'),
                ('Fashion', 'fashion'),
                ('Home & Kitchen', 'home'),
                ('Beauty', 'beauty'),
                ('Books', 'books'),
                ('Sports', 'sports')
            ]
            
            for name, slug in default_categories:
                cur.execute(
                    "INSERT INTO categories(name, slug) VALUES(%s, %s) ON CONFLICT (name) DO NOTHING",
                    (name, slug)
                )
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)
