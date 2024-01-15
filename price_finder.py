import aiohttp
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fuzzywuzzy import fuzz
import spacy
import tldextract
from image_finder import find_product_image
import re

nlp = spacy.load("en_core_web_sm")

async def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

async def find_prices(text_content):
    price_pattern = re.compile(r'\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)')
    prices = price_pattern.findall(text_content)
    return prices

async def get_allowed_substring(website_name, product_name):
    """
    This method defines a dictionary that has each website assigned to its own allowed substring.
    This substring serves as a filter to selectively extract product links.

    E.g. JBHIFI -> '/products/'
         MYER -> '/p/'
         OFFICEWORKS -> '/shop/'

    Returns:
        Substring (str)
    """
    product_name = '-'.join(product_name)

    allowed_substrings = {
        # "jbhifi": '/products/',
        "myer": '/p/',
        "rebelsport": '/p/',
        "nike": '/t/',
        "officeworks": '/shop/officeworks/',
        "davidjones": '/product/',
        "binglee": '/products/',
        "puma": '/pd/',
        "asics": '/en/au/',
        "apple": '/shop/buy-iphone' or '/shop/buy-mac' or '/shop/buy-ipad',
        "culturekings": '/products/',
        "sportshowroom": f'/{product_name}',
        "amazon": f'/s?k={product_name}',
    }

    website_name = website_name or "default"
    substring = allowed_substrings.get(website_name, "default")
    print(f"substring allowed for {website_name} is {substring}.")
    return substring

async def process_url(url, product_name, processed_sublinks=set(), printed_prices=set()):
    if url in processed_sublinks:
        print(f"Skipping already processed URL: {url}")
        return

    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        html_content = await response.text()

        soup = BeautifulSoup(html_content, 'lxml')
        text_content = soup.get_text()

        entities = await extract_entities(text_content)
        # prices = find_prices(text_content)

        # Join the extracted product names into a single string
        extracted_product_names = ' '.join(entity[0] for entity in entities)

        extracted_info = tldextract.extract(url)
        allowed_substring = await get_allowed_substring(extracted_info.domain, product_name)
        # Extract sublinks with allowed substring in the URL
        sublinks = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if allowed_substring in a['href']}
        # Process only new sublinks
        new_sublinks = sublinks - processed_sublinks
        for sublink in new_sublinks:
            if sublink in printed_prices:
                print(f"Skipping already printed price for URL: {sublink}")
                continue
            sublink_response = await session.get(sublink)
            sublink_html_content = await sublink_response.text()
            sublink_soup = BeautifulSoup(sublink_html_content, 'lxml')
            sublink_text_content = sublink_soup.get_text()
            sublink_prices = await find_prices(sublink_text_content)
            url_info = tldextract.extract(url)
            base_url=f"https://www.{url_info.domain}.com.au/"
    
            for sublink_price in sublink_prices:
                sublink_images, alt_text = await find_product_image(sublink, session, base_url)
                for sublink_price in sublink_prices:
                    print(f"Price: ${sublink_price} - URL: {sublink} - Image: {sublink_images} - Alt: {alt_text}")
                    printed_prices.add(sublink)  # Add the sublink to the set of printed prices
                    
        # Add processed sublinks to the set
        processed_sublinks.update(new_sublinks)
