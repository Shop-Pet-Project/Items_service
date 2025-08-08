from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from items_app.infrastructure.config import config


engine = create_async_engine(config.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
