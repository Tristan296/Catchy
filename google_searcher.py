import aiohttp
from googlesearch import search
from google_product_extractor import run
import asyncio
from fuzzywuzzy import fuzz
from price_finder import process_url
from image_finder import find_product_image

query = "keji".split(' ')

def fuzzy_match(query, text):
    # Fuzzy string matching 
    return fuzz.partial_ratio(' '.join(query), text)

async def main():
    for url in search(' '.join(query), tld="co.in", num=10, stop=20, pause=0.1):
        if fuzzy_match(query, url) > 70:
            await process_url(url, query)

if __name__ == "__main__":
    asyncio.run(main())