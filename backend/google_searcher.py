import os
import sys
import aiohttp
from googlesearch import search
import asyncio
from fuzzywuzzy import fuzz
from backend.webScraper import WebCrawler
from flask_cors import CORS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Local 
from . import webScraper
from . import image_finder


query = "Nike air max".split(' ')

def fuzzy_match(query, text):
    # Fuzzy string matching 
    return fuzz.partial_ratio(' '.join(query), text)

async def main(query):
    setFlag = False
    products_data = []

    for url in search(' '.join(query), tld="co.in", num=10, stop=20, pause=0.1):
        if fuzzy_match(query, url) > 70:
            product_data = await WebCrawler.process_url(url, setFlag, query)
            products_data.append(product_data)

    # Store the product data globally
    global global_products_data
    global_products_data = products_data

    return products_data


if __name__ == "__main__":
    asyncio.run(main())