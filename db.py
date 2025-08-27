from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL connection settings
DATABASE_URL = "mysql+pymysql://root:subha12345@localhost/library_db"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Session
SessionLocal = sessionmaker(bind=engine)

# Base for models
Base = declarative_base()
