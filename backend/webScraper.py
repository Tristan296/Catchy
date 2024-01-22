import asyncio
import os
import sys
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urlparse
import tldextract
import yarl
from fuzzywuzzy import fuzz
import re 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from .image_finder import find_product_image
from .priceFinder import PriceScraper

class WebCrawler:
    def __init__(self):
        self.processed_sublinks = set()
    
    @staticmethod        
    async def get_allowed_substring(website_name, product_name, setFlag):
        """
        This method defines a dictionary that has each website assigned to its own allowed substring.
        This substring serves as a filter to selectively extract product links.

        E.g. JBHIFI -> '/products/'
            MYER -> '/p/'
            OFFICEWORKS -> '/shop/'

        Returns:
            Substring (str)
        """
        # product_name = '-'.join(product_name)
        allowed_substrings = {
            "crossroads": '/product',
            "binglee": '/products/',
            # "jd-sports": '/product/', # images not working, and product names are not useful: 'jdsport'
            "footlocker": '/en/product/',
            "insport": '/sale/product/' or '/product/',
            "kogan": '/buy/',
            "officeworks": '/shop/officeworks/p/',
            "davidjones": '/product/',
            "kmart": '/product/',
            "bigw": '/product/',
            "woolworths": '/shop/productdetails/',
            "target": '/p/',
            "ebgames": '/product/',
            "puma": '/au/en/pd/',
            "uniqlo": '/en/products/',
            "gluestore": '/products/',
            "myer": '/p/',
            "rebelsport": '/p/',
            "nike": '/t/',
            "puma": '/pd/', 
            "asics": '/en/au/',
            "culturekings": '/products/',
            "harveynorman": str(product_name)
        }

        # Parse the URL
        parsed_url = urlparse(website_name)

        if parsed_url:
            # Extract the keyword from the hostname:
            #Example: https://www.myer.com.au/p/health.......
            #Will get "myer"
            if(parsed_url.hostname):
                keyword = parsed_url.hostname.split('.')[1]
            else:
                print('Parsed URL has no hostname. Skipping this link.')
                return  
                    

            #Getting the tag from the website 
            #Example: https://www.myer.com.au/p/health.......
            #Will get "/p/"
            # getTag = f'/{parsed_url.path.split("/")[1]}/'
            path_parts = parsed_url.path.split('/')
            if len(path_parts) > 1: #Some links are empty and to prevent index out of bounds I added if statements
                required_part = f'/{path_parts[1]}/'
                getTag = required_part
            else:
                getTag = path_parts

            if getTag in allowed_substrings.values():
                # substring = allowed_substrings.get(website_name, "default")
                print(f"substring allowed for {website_name} is {getTag}.")
                setFlag = True
                return setFlag
            else:
                setFlag = False
                print(f"substring {getTag} not defined for {keyword}.")
                return setFlag

    @staticmethod
    async def process_url(url, setFlag, product_name, socketio,
                          # Default Parameters
                          processed_sublinks=set(), 
                          printed_prices=set(), 
                          product_data=[None, None, None, None]):
        
        """Processes a given URL, extracts allowed substrings 

        Args:
            url (str): The URL to process.
            product_name (str): The name of the product being searched.
            processed_sublinks (set, optional): A set of URLs that have already been processed. Defaults to set().
            printed_prices (set, optional): A set of URLs for which prices have already been printed. Defaults to set().
        """
        if url in processed_sublinks:
            print(f"Skipping already processed URL: {url}")
            return

        async def process_sub_url_wrapper(sublink, session, processed_sublinks, base_url, product_name, setFlag, product_data, socketio):
            return await SublinkProcessor.process_sub_url(sublink, session, processed_sublinks, base_url, product_name, setFlag, product_data, socketio)

        tasks = []

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'lxml', parse_only=SoupStrainer('a'))
            url_info = tldextract.extract(url)
            base_url = urljoin(url, "/")  # Use urljoin for base URL

            for a in soup.find_all('a', href=True):
                sublink_parts = yarl.URL(a['href']).parts
                sublink = urljoin(url, a['href'])
                joined_parts = ' '.join(sublink_parts)

                if fuzz.partial_ratio(product_name, joined_parts) > 40:
                    # Include 'socketio' in the arguments
                    tasks.append(process_sub_url_wrapper(sublink, session, processed_sublinks, base_url, product_name, setFlag, product_data, socketio))

            await asyncio.gather(*tasks)

        return product_data


class SublinkProcessor:
    @staticmethod
    async def process_sub_url(url, session, processed_sublinks, base_url, product_name, setFlag, product_data, socketio):
        """Processes sublinks extracted from the main URL, prints product details, and updates processed sublinks set.

        Args:
            url (str): The main URL from which sublinks are derived.
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content of the main URL.
            session (aiohttp.ClientSession): The Aiohttp client session.
            allowed_substring (str): The allowed substring used to filter sublinks.
            processed_sublinks (set): A set of URLs that have already been processed.
            base_url (str): base url of website with its domain derived from tldextract
            setFlag: If price exists switch the flag on me. This will print items that have prices on frontend

        Note:
            This function fetches sublinks, processes them, extracts prices and images, and prints product details.
            It then updates the set of processed sublinks.
        """
        
        product_name = str(product_name).replace(' ', '-')
        sublinks = set()

        async with session.get(url) as sublink_response:
            sublink_html_content = await sublink_response.text()

        sublink_soup = BeautifulSoup(sublink_html_content, 'lxml')
        sublink_text_content = sublink_soup.get_text()

        for a in sublink_soup.find_all('a', href=True):
            sublink_parts = yarl.URL(a['href']).parts
            joined_parts = ' '.join(sublink_parts)

            if fuzz.partial_ratio(product_name, joined_parts) > 40:
                sublinks.add(urljoin(url, a['href']))

        new_sublinks = sublinks - processed_sublinks

        for sublink in new_sublinks:
            sublink_tags = await WebCrawler.get_allowed_substring(sublink, sublink, setFlag)

            if sublink and sublink_tags == True:
                price_scraper = PriceScraper(sublink, sublink_soup)
                sublink_price, innermost_price_element = await price_scraper.find_product_name_element()
                sublink_image_url, sublink_image_tag = await find_product_image(sublink, session, base_url)
                
                if sublink_price and sublink_image_tag:
                    print_product_details(sublink, sublink_image_url, sublink_image_tag, sublink_price)
                    # Update the following line to exclude 'socketio'
                    socketio.emit('product_data', {"status": "success", "products": [[sublink, sublink_price, sublink_image_url, sublink_image_tag]]})

        processed_sublinks.update(new_sublinks)
        return product_data
    
def print_product_details(link, image_url, image_tag, price):
    print("Found Product details:")
    print(f"Link: {link}")
    print(f"Image src: {image_url}")
    print(f"Image alt: {image_tag}")
    print(f"Price: {price}\n\n")