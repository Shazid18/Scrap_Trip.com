import scrapy
import json
import re
import random

class HotelDetailsSpider(scrapy.Spider):
    name = "hotel_details_spider"
    start_urls = [
        'https://uk.trip.com/hotels/?locale=en-GB&curr=GBP',
    ]

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

                        yield {
                            'City': city_name,
                            'Title': hotel_name,
                            'Location': hotel_address,
                            'Price': price,
                            'Images': hotel_img,
                            'Rating': comment_score,
                            'Room Type': physical_room_name,
                            'Latitude': lat,
                            'Longitude': lng
                        }

                except json.JSONDecodeError:
                    self.logger.error("Failed to decode JSON data.")
