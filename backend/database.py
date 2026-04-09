import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./support_hub.db")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "support_hub_logs")

# PostgreSQL / SQLite setup
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[MONGO_DB_NAME]

    async def close(self):
        if self.client:
            self.client.close()


mongodb = MongoDB()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
