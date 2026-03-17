
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.article import NormalizedArticle
from app.core.config import settings

async def test_db():
    print(f"Connecting to: {settings.SQLALCHEMY_DATABASE_URI}")
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # Try to query articles
            from sqlalchemy import select
            result = await session.execute(select(NormalizedArticle).limit(1))
            article = result.scalar_one_or_none()
            if article:
                print(f"Found article: {article.headline}")
                print(f"Tags: {article.tags}")
            else:
                print("No articles found.")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_db())
