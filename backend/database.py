from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

# Get database URL from environment variable with asyncpg driver
DATABASE_URL = getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/fatakeshto?sslmode=require"
)

# Create async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

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