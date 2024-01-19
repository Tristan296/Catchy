import asyncio
import io
import re
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fuzzywuzzy import fuzz
import requests
import numpy as np

async def find_product_image(link, session, base_url):
    async with session.get(link) as response:
        # Ensure that the response status is OK
        if response.status == 200:
            # Read the HTML content from the response
            html = await response.text()

            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(html, 'lxml')

            # Get the product name
            product_name = await extract_product_name(link)

            # Find all img tags
            images = soup.find_all('img')

            for image in images:
                # Get the src and alt attributes
                src_value = image.get('src') or image.get('data-src')
                alt = image.get('alt', '').lower()

                # Use fuzzy matching for alt attribute
                ratio = fuzz.ratio(product_name, alt)

                if ratio > 40:
                    #Join the base url with the found image url
                    src_value = urljoin(base_url, src_value)
                    
                    print(f"Found image with matching alt: {src_value}")

                    return src_value, alt

    return None, None

async def extract_product_name(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the product name from the last segment of the path
    path_segments = parsed_url.path.strip('/').split('/')
    if path_segments:
        product_name = path_segments[-1]

        # Remove any trailing characters like ".html" or digits
        product_name = re.sub(r'(\.html\d+)$', '', product_name)

        # Split the product name into parts and join them
        product_name = '-'.join(filter(None, product_name.split('-')))

        return product_name

    return ""  # Return an empty string if no product name is found
