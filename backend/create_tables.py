import asyncio
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine
from backend.models import Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    try:
        await create_tables()
        print('All database tables have been created successfully!')
    except Exception as e:
        print(f'Error creating tables: {str(e)}')

if __name__ == '__main__':
    asyncio.run(main())