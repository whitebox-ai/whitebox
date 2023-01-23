from whitebox.core.settings import get_settings
import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from whitebox.entities.Base import Base
from whitebox.schemas.user import UserCreateDto

from whitebox import crud
from whitebox.utils.passwords import encrypt_api_key
from whitebox.utils.logger import cronLogger as logger
import os

from secrets import token_hex

settings = get_settings()
database = databases.Database(settings.DATABASE_URL)
engine = sqlalchemy.create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def connect():
    """
    Connect to DB
    """
    Base.metadata.create_all(engine)
    db = SessionLocal()
    if not os.getenv("ENV") == "test":
        admin_exists = crud.users.get_first_by_filter(db=db, username="admin")
        if not admin_exists:
            api_key = token_hex(32)
            if settings.SECRET_KEY:
                secret_key = settings.SECRET_KEY.encode()
                api_key = encrypt_api_key(api_key, secret_key)

            obj_in = UserCreateDto(username="admin", api_key=api_key)
            crud.users.create(db=db, obj_in=obj_in)
            logger.info(f"Created username: admin, API key: {api_key}")
    await database.connect()


async def close():
    """
    Close DB Connection
    """
    await database.disconnect()
    # logging.info("Closed connection with DB")
