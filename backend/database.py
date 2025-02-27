from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

# Get database URL from environment variable with asyncpg driver
from urllib.parse import quote_plus

# Get database URL from environment variable with asyncpg driver
DATABASE_URL = getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://neondb_owner:{quote_plus('npg_efE9hVpwUM5n')}@ep-patient-truth-a15jezae-pooler.ap-southeast-1.aws.neon.tech/neondb"
)

import ssl

# Create SSL context with certificate verification disabled
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async SQLAlchemy engine with SSL configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "ssl": ssl_context
    }
)

# Create AsyncSessionLocal class
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create Base class for declarative models
Base = declarative_base()

# Dependency to get async database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()