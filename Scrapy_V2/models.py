import os
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up base directory for images
BASE_DIR = os.path.join(os.getcwd(), "hotel_images")
os.makedirs(BASE_DIR, exist_ok=True)

Base = declarative_base()

# Define the Hotel model
class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    image_path = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    room_type = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

# Initialize the database
DATABASE_URL = "postgresql://user:password@postgres_container:5432/scrapy_db"
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
