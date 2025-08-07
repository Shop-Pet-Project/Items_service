class Config:
    DATABASE_URL: str = "sqlite+aiosqlite:///src/items_app/infrastructure/db.sqlite3"

config = Config()