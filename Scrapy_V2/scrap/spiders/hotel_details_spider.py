import scrapy
import json
import re
import random
import os
import requests
from sqlalchemy.orm import sessionmaker
from models import Hotel, SessionLocal, BASE_DIR

class HotelDetailsSpider(scrapy.Spider):
    name = "hotel_details_spider"
    start_urls = [
        'https://uk.trip.com/hotels/?locale=en-GB&curr=GBP',
    ]

    def __init__(self):
        # Initialize database session
        self.db = SessionLocal()

    def parse(self, response):
        # Extract all <script> tags from the response
        scripts = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]//text()").getall()

        for script in scripts:
            match = re.search(r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    data = json.loads(json_str)

                    # Extract inbound and outbound cities randomly
                    init_data = data.get("initData", {})
                    htls_data = init_data.get("htlsData", {})
                    cities = htls_data.get("inboundCities", []) + htls_data.get("outboundCities", [])
                    
                    if cities:
                        random_city = random.choice(cities)
                        city_id = random_city.get("id")
                        if city_id:
                            city_url = f'https://us.trip.com/hotels/list?city={city_id}'
                            yield scrapy.Request(url=city_url, callback=self.parse_city_page)
                            yield {'city_url': city_url}

                except json.JSONDecodeError:
                    self.logger.error("Failed to decode JSON data.")

    def parse_city_page(self, response):
        scripts = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]//text()").getall()

        for script in scripts:
            match = re.search(r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    data = json.loads(json_str)
                    init_data = data.get("initData", {})
                    first_page_list = init_data.get("firstPageList", {})
                    hotel_list = first_page_list.get("hotelList", [])

                    for hotel in hotel_list:
                        hotel_basic_info = hotel.get("hotelBasicInfo", {})
                        comment_info = hotel.get("commentInfo", {})
                        room_info = hotel.get("roomInfo", {})
                        position_info = hotel.get("positionInfo", {})
                        coordinate = position_info.get("coordinate", {})

                        # Extract details
                        city_name = position_info.get("cityName", None)
                        hotel_name = hotel_basic_info.get("hotelName", None)
                        hotel_address = position_info.get("positionName", None)
                        price = hotel_basic_info.get("price", None)
                        hotel_img = hotel_basic_info.get("hotelImg", None)
                        comment_score = comment_info.get("commentScore", None)
                        physical_room_name = room_info.get("physicalRoomName", None)
                        lat = coordinate.get("lat", None)
                        lng = coordinate.get("lng", None)

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
                        image_path = os.path.join(BASE_DIR, f"{hotel_name.replace(' ', '_')}.jpg") if hotel_name else ""
                        if hotel_img:
                            try:
                                response = requests.get(hotel_img, stream=True)
                                if response.status_code == 200:
                                    with open(image_path, "wb") as img_file:
                                        img_file.write(response.content)
                            except requests.RequestException as e:
                                self.logger.error(f"Failed to download image for {hotel_name}: {e}")
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

                        yield {
                            'City': city_name,
                            'Title': hotel_name,
                            'Location': hotel_address,
                            'Price': price,
                            'Images': image_path,
                            'Rating': comment_score,
                            'Room Type': physical_room_name,
                            'Latitude': lat,
                            'Longitude': lng
                        }

                except json.JSONDecodeError:
                    self.logger.error("Failed to decode JSON data.")


    def close(self, reason):
        # Close database session
        self.db.close()
