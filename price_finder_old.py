import asyncio
import os
import time
import aiohttp
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import Request
from urllib.parse import urljoin, urlparse
import re
from yarl import URL
from fuzzywuzzy import fuzz


async def find_product_name_element(link, soup):
    """Extracts html elements containing product name elements entities matching product name from product urls.

    Args:
        product_name (str)
        links (list): A list of URLs to process.

    Prints:
        Matching HTML element 
    """
    if not isinstance(link, str):
        print("Skipping processing for link, it's not a string:", link)
        return None, None
  
    product_name = await extract_product_name(link)

    if product_name is None:
        print(f"Skipping processing for {link} as product name is None")
        return None, None
    
    product_name = str(product_name).split('-')

    print(f"finding the price for {product_name} in {link}")

    matched_tag = soup.find(lambda tag: fuzz.partial_ratio(product_name, tag.get_text()) > 40 if tag.get_text() else False)

    price, innermost_child = await find_product_price(matched_tag, soup)
    if price:
        return price, innermost_child

    else:
        print("Price couldn't be found. Trying to find the first price in the website using regex.")
        first_price = await find_first_price_with_regex(soup)
        if first_price:
            return f"${first_price}", None
        else:
            print("No price found on the website.")
            return None, None

async def find_first_price_with_regex(soup):
    # Find the first price in the website using a regular expression
    price_pattern = re.compile(r'^\d+(,\d{1,2})?$')  # Adjust the regex pattern based on your price format
    first_price_match = soup.find(string=price_pattern)

    if first_price_match:
        return first_price_match.strip()
    else:
        return None
                    
async def find_product_price(matched_tag, soup):
    current_tag = matched_tag

    while current_tag:
        next_sibling = current_tag.findNext('div')

        if next_sibling:
            innermost_child = next_sibling.find(lambda tag: not tag.find_all(), recursive=False)

            if innermost_child:
                price_text = innermost_child.text.strip()

                if is_valid_price(price_text):
                   #  print("Price:", price_text)
                    return price_text, innermost_child

        current_tag = next_sibling
    
    
    return None, None

def is_valid_price(text):
    # Use a regular expression to check if the text matches a typical price pattern
    price_pattern = re.compile(r'^\$\d+(\.\d{1,2})?$')  # Assumes a simple dollar amount (e.g., $10 or $10.50)
    return bool(price_pattern.match(text))

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