from app.db.session import async_session_maker


async def get_session():
    async with async_session_maker() as session:
        yield session
