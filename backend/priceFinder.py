import asyncio
import os
import sys
import aiohttp
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import Request
from urllib.parse import urljoin, urlparse
import re
from yarl import URL
from fuzzywuzzy import fuzz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

class PriceScraper:
    def __init__(self, link, soup):
        self.link = link
        self.soup = soup

    async def find_product_name_element(self):
        if not isinstance(self.link, str):
            print("Skipping processing for link, it's not a string:", self.link)
            return None, None

        matched_tag = self.soup.find(lambda tag: fuzz.partial_ratio(self.link, tag.get_text()) > 40 if tag.get_text() else False)
        price, innermost_child = await self.find_product_price(matched_tag)

        if price:
            return price, innermost_child
        else:
            print("Price couldn't be found. Trying to find the first price in the website using regex.")
            first_price = await self.find_first_price_with_regex()
            if first_price:
                return f"${first_price}", None
            else:
                print("No price found on the website.")
                return None, None

    async def find_first_price_with_regex(self):
        # Find the first price in the website using a regular expression
        price_pattern = re.compile(r'^\d+(,\d{1,2})?$')
        first_price_match = self.soup.find(string=price_pattern)

        if first_price_match:
            return first_price_match.strip()
        else:
            return None

    async def find_product_price(self, matched_tag):
        current_tag = matched_tag

        while current_tag:
            next_sibling = current_tag.findNext('div')

            if next_sibling:
                innermost_child = next_sibling.find(lambda tag: not tag.find_all(), recursive=False)

                if innermost_child:
                    price_text = innermost_child.text.strip()

                    if self.is_valid_price(price_text):
                        return price_text, innermost_child

            current_tag = next_sibling

        return None, None

    def is_valid_price(self, text):
        # Use a regular expression to check if the text matches a typical price pattern
        price_pattern = re.compile(r'^\$\d+(\.\d{1,2})?$')  # Assumes a simple dollar amount (e.g., $10 or $10.50)
        return bool(price_pattern.match(text))


class ProductNameExtractor:
    @staticmethod
    def extract_product_name(url_parts):
        # Extract the product name from the second element onward in the path
        if url_parts:
            product_name = url_parts[::1]
            return product_name
        return ""  # Return an empty string if no product name is found