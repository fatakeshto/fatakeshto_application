from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Base, User, UserRole
from database import engine, AsyncSessionLocal
from utils import get_password_hash
import asyncio

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create admin user if it doesn't exist
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        result = await session.execute(
            select(User).where(User.username == 'admin')
        )
        admin_user = result.scalars().first()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@fatakeshto.com',
                hashed_password=get_password_hash('Admin@123'),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print('Admin user created successfully')
        else:
            print('Admin user already exists')

if __name__ == '__main__':
    asyncio.run(init_db())