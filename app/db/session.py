from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

#creating the connection managera:
engine=create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


#a factory for database sessions:
SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

