import os
import requests
from sqlalchemy.orm import sessionmaker
from models import Hotel, SessionLocal, BASE_DIR

class HotelDetailsPipeline:
    def __init__(self):
        # Initialize database session
        self.db = SessionLocal()

    def process_item(self, item, spider):
        # Extract relevant fields from the item
        city_name = item.get('City')
        hotel_name = item.get('Title')
        hotel_address = item.get('Location')
        price = item.get('Price')
        image_path = item.get('Images')
        comment_score = item.get('Rating')
        physical_room_name = item.get('Room Type')
        lat = item.get('Latitude')
        lng = item.get('Longitude')

        # Handle missing or empty values
        city_name = city_name if city_name and city_name != '' else None
        hotel_name = hotel_name if hotel_name and hotel_name != '' else None
        hotel_address = hotel_address if hotel_address and hotel_address != '' else None
        physical_room_name = physical_room_name if physical_room_name and physical_room_name != '' else None

        # Handle numerical fields with proper conversion to None for missing values
        price = float(price) if price and price != '' else None
        comment_score = float(comment_score) if comment_score and comment_score != '' else None
        lat = float(lat) if lat and lat != '' else None
        lng = float(lng) if lng and lng != '' else None

        # Download image and save to file
        if hotel_name:
            image_path = os.path.join(BASE_DIR, f"{hotel_name.replace(' ', '_')}.jpg") if image_path else ""
            if image_path:
                try:
                    response = requests.get(image_path, stream=True)
                    if response.status_code == 200:
                        with open(image_path, "wb") as img_file:
                            img_file.write(response.content)
                except requests.RequestException as e:
                    spider.logger.error(f"Failed to download image for {hotel_name}: {e}")
                    image_path = ""  # If image fails, set to an empty string

        # Store data in the database
        hotel_entry = Hotel(
            city=city_name,
            title=hotel_name,
            location=hotel_address,
            price=price,
            image_path=image_path,
            rating=comment_score,
            room_type=physical_room_name,
            latitude=lat,
            longitude=lng
        )

        self.db.add(hotel_entry)
        self.db.commit()

        return item

    def close_spider(self, spider):
        # Close database session
        self.db.close()
