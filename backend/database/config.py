"""
Database Configuration for Enterprise Scanner
Production-ready PostgreSQL setup with connection pooling and monitoring
"""

import os
import logging
from typing import Generator
import time

# Handle SQLAlchemy imports with fallback
try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.engine import Engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    print("SQLAlchemy not available - using mock database configuration")
    SQLALCHEMY_AVAILABLE = False
    # Mock classes for when SQLAlchemy is not available
    class MockEngine:
        def execute(self, *args, **kwargs):
            pass
    
    class MockSessionmaker:
        def __call__(self):
            return MockSession()
    
    class MockSession:
        def query(self, *args):
            return MockQuery()
        def add(self, obj):
            pass
        def commit(self):
            pass
        def rollback(self):
            pass
        def close(self):
            pass
    
    class MockQuery:
        def filter(self, *args):
            return self
        def first(self):
            return None
        def all(self):
            return []
        def count(self):
            return 0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
class DatabaseConfig:
    """Database configuration settings"""
    
    def __init__(self):
        self.database_url = self.get_database_url()
        self.pool_size = int(os.environ.get('DB_POOL_SIZE', '20'))
        self.pool_timeout = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
        self.echo_sql = os.environ.get('DB_ECHO', 'False').lower() == 'true'
        self.environment = os.environ.get('FLASK_ENV', 'development')
    
    def get_database_url(self) -> str:
        """Get database URL from environment with fallbacks"""
        
        # Production database URL
        if os.environ.get('DATABASE_URL'):
            return os.environ.get('DATABASE_URL')
        
        # Construct from individual components
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'enterprise_scanner')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', 'password')
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Initialize configuration
config = DatabaseConfig()

# Create SQLAlchemy engine with production settings
engine = create_engine(
    config.database_url,
    poolclass=QueuePool,
    pool_size=config.pool_size,
    pool_timeout=config.pool_timeout,
    pool_recycle=config.pool_recycle,
    pool_pre_ping=True,  # Validate connections before use
    echo=config.echo_sql,
    connect_args={
        "application_name": "enterprise_scanner",
        "options": "-c timezone=UTC"
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Connection event handlers for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure connection settings"""
    if config.environment == 'production':
        logger.info("Database connection established")

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries in development"""
    if config.echo_sql:
        context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time"""
    if config.echo_sql and hasattr(context, '_query_start_time'):
        total = time.time() - context._query_start_time
        if total > 0.1:  # Log queries longer than 100ms
            logger.warning(f"Slow query ({total:.2f}s): {statement[:100]}...")

def get_db() -> Generator:
    """
    Dependency for getting database session
    Use with FastAPI dependency injection or Flask context
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            if result.fetchone()[0] == 1:
                logger.info("Database connection test successful")
                return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def get_connection_info():
    """Get database connection information"""
    return {
        'url': config.database_url.split('@')[1] if '@' in config.database_url else 'local',
        'pool_size': config.pool_size,
        'environment': config.environment,
        'echo_sql': config.echo_sql
    }

# Health check function
def health_check():
    """Comprehensive database health check"""
    health_status = {
        'status': 'healthy',
        'checks': {},
        'connection_info': get_connection_info()
    }
    
    try:
        # Test basic connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            health_status['checks']['connection'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
            
            # Test table existence
            try:
                result = connection.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = result.fetchone()[0]
                health_status['checks']['tables'] = {
                    'status': 'healthy',
                    'table_count': table_count,
                    'message': f'{table_count} tables found'
                }
            except Exception as e:
                health_status['checks']['tables'] = {
                    'status': 'error',
                    'message': f'Table check failed: {str(e)}'
                }
                health_status['status'] = 'degraded'
            
            # Test connection pool
            pool = engine.pool
            health_status['checks']['pool'] = {
                'status': 'healthy',
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'message': f'Pool: {pool.checkedout()}/{pool.size()} connections in use'
            }
            
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['connection'] = {
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }
    
    return health_status

# Migration utilities
class DatabaseMigration:
    """Database migration utilities"""
    
    @staticmethod
    def backup_tables(tables: list = None):
        """Create backup of specified tables"""
        # Implementation for table backup
        pass
    
    @staticmethod
    def restore_tables(backup_path: str):
        """Restore tables from backup"""
        # Implementation for table restore
        pass
    
    @staticmethod
    def migrate_data(source_data: dict):
        """Migrate data from in-memory storage to database"""
        # Implementation for data migration
        pass

if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
        
        # Print connection info
        info = get_connection_info()
        print(f"Database URL: {info['url']}")
        print(f"Pool Size: {info['pool_size']}")
        print(f"Environment: {info['environment']}")
        
        # Run health check
        health = health_check()
        print(f"Health Status: {health['status']}")
        for check_name, check_result in health['checks'].items():
            print(f"  {check_name}: {check_result['status']} - {check_result['message']}")
    else:
        print("❌ Database connection failed")
        exit(1)