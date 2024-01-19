import aiohttp
from googlesearch import search
import asyncio
from fuzzywuzzy import fuzz

# Local 
from google_product_extractor import run
from webScraper import WebCrawler
from image_finder import find_product_image

query = "Nike air max".split(' ')

def fuzzy_match(query, text):
    # Fuzzy string matching 
    return fuzz.partial_ratio(' '.join(query), text)

async def main():
    setFlag = False
    for url in search(' '.join(query), tld="co.in", num=10, stop=20, pause=0.1):
        if fuzzy_match(query, url) > 70:
            await WebCrawler.process_url(url, setFlag, query)

if __name__ == "__main__":
    asyncio.run(main())