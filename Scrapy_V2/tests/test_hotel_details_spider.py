import unittest
from unittest.mock import Mock, patch
from scrapy.http import TextResponse, Request
from scrap.spiders.hotel_details_spider import HotelDetailsSpider
import json
import re

class TestHotelDetailsSpider(unittest.TestCase):
    def setUp(self):
        self.spider = HotelDetailsSpider()

    def create_mock_response(self, body, url='https://uk.trip.com/hotels/'):
        return TextResponse(
            url=url,
            body=body.encode('utf-8'),
            encoding='utf-8'
        )

    def test_parse_empty_response(self):
        """Test parsing with empty response"""
        response = self.create_mock_response("")
        results = list(self.spider.parse(response))
        self.assertEqual(len(results), 0)

    def test_parse_with_valid_data(self):
        """Test parsing with valid JSON data"""
        mock_script = """
        <script>
            window.IBU_HOTEL = {
                "initData": {
                    "htlsData": {
                        "inboundCities": [
                            {"id": "1", "name": "London"},
                            {"id": "2", "name": "Paris"}
                        ],
                        "outboundCities": [
                            {"id": "3", "name": "New York"}
                        ]
                    }
                }
            };
        </script>
        """
        response = self.create_mock_response(mock_script)
        results = list(self.spider.parse(response))

        # Check if we got any results
        self.assertTrue(len(results) > 0)

        # Check if we have both Request objects and dictionaries
        request_objects = [r for r in results if isinstance(r, Request)]
        dict_objects = [r for r in results if isinstance(r, dict)]

        # We should have at least one Request object
        self.assertTrue(len(request_objects) > 0)

        # We should have at least one dictionary with city_url
        self.assertTrue(len(dict_objects) > 0)
        self.assertTrue(any('city_url' in d for d in dict_objects))

        # Check if the Request URLs are properly formed
        for request in request_objects:
            self.assertTrue('hotels/list?city=' in request.url)

    def test_parse_city_page(self):
        """Test parsing city page with hotel data"""
        mock_city_data = """
        <script>
            window.IBU_HOTEL = {
                "initData": {
                    "firstPageList": {
                        "hotelList": [{
                            "hotelBasicInfo": {
                                "hotelName": "Test Hotel",
                                "price": 100,
                                "hotelImg": "test.jpg"
                            },
                            "commentInfo": {
                                "commentScore": 4.5
                            },
                            "roomInfo": {
                                "physicalRoomName": "Deluxe Room"
                            },
                            "positionInfo": {
                                "cityName": "London",
                                "positionName": "123 Test Street",
                                "coordinate": {
                                    "lat": 51.5074,
                                    "lng": -0.1278
                                }
                            }
                        }]
                    }
                }
            };
        </script>
        """
        response = self.create_mock_response(mock_city_data, 'https://us.trip.com/hotels/list?city=1')
        results = list(self.spider.parse_city_page(response))

        self.assertEqual(len(results), 1)
        hotel_data = results[0]
        self.assertEqual(hotel_data['Title'], 'Test Hotel')
        self.assertEqual(hotel_data['City'], 'London')
        self.assertEqual(hotel_data['Price'], 100)
        self.assertEqual(hotel_data['Rating'], 4.5)
        self.assertEqual(hotel_data['Room Type'], 'Deluxe Room')
        self.assertEqual(hotel_data['Location'], '123 Test Street')
        self.assertEqual(hotel_data['Latitude'], 51.5074)
        self.assertEqual(hotel_data['Longitude'], -0.1278)

    def test_parse_invalid_json(self):
        """Test parsing with invalid JSON data"""
        mock_invalid_script = """
        <script>
            window.IBU_HOTEL = {
                invalid json data
            };
        </script>
        """
        response = self.create_mock_response(mock_invalid_script)
        results = list(self.spider.parse(response))
        self.assertEqual(len(results), 0)

    @patch('scrapy.Request')
    def test_request_generation(self, mock_request):
        """Test if correct requests are generated"""
        mock_script = """
        <script>
            window.IBU_HOTEL = {
                "initData": {
                    "htlsData": {
                        "inboundCities": [
                            {"id": "1", "name": "London"}
                        ],
                        "outboundCities": []
                    }
                }
            };
        </script>
        """
        response = self.create_mock_response(mock_script)
        list(self.spider.parse(response))

        # Verify that Request was called with correct URL
        self.assertTrue(
            any('city=1' in str(call) for call in mock_request.call_args_list)
        )


if __name__ == '__main__':
    unittest.main()
