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

    # uses YARL to get the raw parts from the url and get the product name from it 
    # E.g. https://www.example.com/BUZIO-Stainless-Bottle-Vacuum-Insulated/dp/B07R3HYDVW/
    # Returns: ('BUZIO-Stainless-Bottle-Vacuum-Insulated', 'dp', 'B07R3HYDVW', '')

    # url_parts_list = URL(link).parts
    # print("parts list: ", url_parts_list)
    # url_info = [extract_product_name(url_parts) for url_parts in url_parts_list]

    matched_tag = soup.find(lambda tag: fuzz.partial_ratio(link, tag.get_text()) > 40 if tag.get_text() else False)
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

def extract_product_name(url_parts):
    # Extract the product name from the second element onward in the path
    if url_parts:
        product_name = url_parts[::1]
        return product_name

    return ""  # Return an empty string if no product name is found
