import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tldextract
from image_finder import find_product_image
import re 

async def find_prices(text_content):
    """
    Find prices in the given soup using a regular expression pattern.

    Args:
        text_content (str): The sublink's soup content

    Returns:
        list: A list of strings of the found prices.
    """
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
        "myer": '/p/',
        "rebelsport": '/p/',
        "nike": '/t/',
        "davidjones": '/product/',
        "binglee": '/products/',
        "puma": '/pd/',
        "asics": '/en/au/',
        "culturekings": '/products/',
    }

    website_name = website_name or "default"
    substring = allowed_substrings.get(website_name, "default")
    print(f"substring allowed for {website_name} is {substring}.")
    return substring


async def process_url(url, product_name, processed_sublinks=set(), printed_prices=set()):
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

    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        html_content = await response.text()
        soup = BeautifulSoup(html_content, 'lxml')
        url_info = tldextract.extract(url)

        allowed_substring = await get_allowed_substring(url_info.domain, product_name)
        
        await process_sub_url(url, soup, session, allowed_substring, processed_sublinks, f"https://www.{url_info.domain}.com.au/")


async def process_sub_url(url, soup, session, allowed_substring, processed_sublinks, base_url):
    """Processes sublinks extracted from the main URL, prints product details, and updates processed sublinks set.

    Args:
        url (str): The main URL from which sublinks are derived.
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content of the main URL.
        session (aiohttp.ClientSession): The Aiohttp client session.
        allowed_substring (str): The allowed substring used to filter sublinks.
        processed_sublinks (set): A set of URLs that have already been processed.
        base_url (str): base url of website with its domain derived from tldextract

    Note:
        This function fetches sublinks, processes them, extracts prices and images, and prints product details.
        It then updates the set of processed sublinks.
    """
    sublinks = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if allowed_substring in a['href']}
    # Process only new sublinks
    new_sublinks = sublinks - processed_sublinks
    
    for sublink in new_sublinks:
        sublink_response = await session.get(sublink)
        sublink_html_content = await sublink_response.text()
        sublink_soup = BeautifulSoup(sublink_html_content, 'lxml')
        sublink_text_content = sublink_soup.get_text()

        # gets prices for sublinks (returns array of prices)
        sublink_prices = await find_prices(sublink_text_content)

        # Goes through found prices array and gets the images
        for sublink_price in sublink_prices:
            sublink_images, alt_text = await find_product_image(sublink, session, base_url)
            print(f"Price: ${sublink_price} - URL: {sublink} - Image: {sublink_images} - Alt: {alt_text}")
                
    # Add processed sublinks to the set
    processed_sublinks.update(new_sublinks)