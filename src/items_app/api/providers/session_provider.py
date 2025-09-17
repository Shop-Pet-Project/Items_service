from items_app.infrastructure.postgres.database import async_session


# --- Получение сессии базы данных ---
async def get_session():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
