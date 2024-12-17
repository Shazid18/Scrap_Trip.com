# Trip.com Hotel Scraper

 ## Table of Contents
  
  1. [Project Overview](#project-overview)
  2. [Features](#features)
  3. [Project Structure](#project-structure)
  4. [Getting Started](#getting-started)
     - [Dependencies](#dependencies)
     - [Installation](#installation)

## Project Overview

This project is designed to scrape hotel data from Trip.com using Scrapy and store the extracted data into a PostgreSQL database. The scraper gathers hotel details, including the title, rating, location, latitude, longitude, room type, price, and images from randomly selected cities. It uses SQLAlchemy for database interaction, and images are stored locally in a designated folder with their references saved in the database.




## Features

- **Scraping property data such as title, rating, location, latitude, longitude, room type, price, and images**

- **Storing the scraped data in a PostgreSQL database using SQLAlchemy**

- **Automatically creating the necessary tables in the database**

- **Saving images to a file directory and storing the image paths in the database for later retrieval**


## Project Structure
  
  ```plaintext

     Scrapy_project/
        ├── Scrapy_V2/
        │   ├── __pycache__/
        │   ├── hotel_images/
        │   ├── scrap/
        │   │   ├── __pycache__/
        │   │   ├── spiders/
        │   │   │   ├── __pycache__/
        │   │   │   ├── __init__.py
        │   │   │   └── hotel_details_spider.py
        │   │   ├── __init__.py
        │   │   ├── items.py
        │   │   ├── middlewares.py
        │   │   ├── pipelines.py
        │   │   └── settings.py
        │   ├── Dockerfile
        │   ├── docker-compose.yml
        │   ├── models.py
        │   ├── requirements.txt
        │   └── scrapy.cfg
        ├── .gitignore
        ├── help.txt
        └── requirements.txt

  ```




## Getting Started


### Dependencies

This project requires the following Python packages:

- **Python 3.x**
- **Scrapy**
- **SQLAlchemy**
- **PostgreSQL**
- **psycopg2-binary**


### Installation
  
  1. Clone the repository:
     ```bash
     git clone https://github.com/Shazid18/Scrap_Trip.com.git
     ```
     ```bash
     cd Scrap_Trip.com
     ```
  
  2. Set up a virtual environment:
     ```bash
     python3 -m venv venv
     ```
     
  3. Activate the virtual environment:
     ```bash
     source venv/bin/activate   # On Windows: venv\Scripts\activate
     ```
  
  4. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     
  5. Run Docker:
     ```bash
     cd Scrapy_v2
     ```
     ```bash
     docker-compose up --build
     ```
Now it will start Scrape Data from https://uk.trip.com/hotels/?locale=en-GB&curr=GBP and store those data into Postgres Database. And the Hotel images will store in `hotel_images\` directory in you local storage.

### Access pgAdmin to visualize the Postgres Database:
-  Open your browser and go to http://localhost:5050
- Login with the credentials:
    - Username: admin@admin.com
    - Password: admin
- Configure PostgreSQL in pgAdmin:
    - Register server in pgAdmin:
        - Name: PostgreSQL (or any name)
        - Host: db (service name in docker-compose.yml)
        - Port: 5432
        - Username: user
        - Password: password

  Now you can visualize the Postgres Database and see the Scrape data.
### Shut down the Docker containers:
- When done, you can shut down the containers with:
    ```bash
    docker-compose down
    ```
### Start Docker containers again:
- If you need to restart the containers, simply run:
    ```bash
    docker-compose up
    ```
To Scrape another city's Hotel information you need to repeat the Docker `Shut` and `Start` process.
