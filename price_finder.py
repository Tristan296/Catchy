import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tldextract
import yarl
from image_finder import find_product_image
import re 
from fuzzywuzzy import fuzz
from price_finder_old import find_product_name_element


# async def get_allowed_substring(website_name, product_name):
#     """
#     This method defines a dictionary that has each website assigned to its own allowed substring.
#     This substring serves as a filter to selectively extract product links.

#     E.g. JBHIFI -> '/products/'
#          MYER -> '/p/'
#          OFFICEWORKS -> '/shop/'

#     Returns:
#         Substring (str)
#     """
#     product_name = '-'.join(product_name)

#     allowed_substrings = {
#         "binglee": '/products/',
#         "jd-sports": '/product/',
#         "footlocker": '/en/product/',
#         "insport": '/sale/product/' or '/product/',
#         "kogan": '/buy/',
#         "officeworks": '/shop/officeworks/p/',
#         "davidjones": '/product/',
#         "kmart": '/product/',
#         "bigw": '/product/',
#         "woolworths": '/shop/productdetails/',
#         "target": '/p/',
#         "ebgames": '/product/',
#         "puma": '/au/en/pd/',
#         "uniqlo": '/en/products/',
#         "gluestore": '/products/',
#         "myer": '/p/',
#         "rebelsport": '/p/',
#         "nike": '/t/',
#         "puma": '/pd/', 
#         "asics": '/en/au/',
#         "culturekings": '/products/',
#         "harveynorman": str(product_name)
#     }

#     website_name = website_name or "default"
#     substring = allowed_substrings.get(website_name, "default")
#     print(f"substring allowed for {website_name} is {substring}.")
#     return substring


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

        # allowed_substring = await get_allowed_substring(url_info.domain, product_name)

        await process_sub_url(url, soup, session, processed_sublinks, f"https://www.{url_info.domain}.com.au/", product_name)


async def process_sub_url(url, soup, session, processed_sublinks, base_url, product_name):
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
    
    
    product_name = str(product_name).replace(' ', '-')

    # 
    sublinks = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if fuzz.partial_ratio(product_name, yarl.URL(a['href']).path.replace('/', '-')) > 40}
    # Process only new sublinks
    new_sublinks = sublinks - processed_sublinks
    
    for sublink in new_sublinks:

        sublink_response = await session.get(sublink)
        sublink_html_content = await sublink_response.text()
        sublink_soup = BeautifulSoup(sublink_html_content, 'lxml')
        sublink_text_content = sublink_soup.get_text()

        # gets prices for sublinks (returns array of prices)
        sublink_price, innermost_price_element = await find_product_name_element(sublink, sublink_soup)
        
        if sublink_price:
            print("Found Product details:")
            print(f"Link: {sublink}")
            print(f"Price: {sublink_price}\n\n")


    # Add processed sublinks to the set
    processed_sublinks.update(new_sublinks)


async def extract_product_name(url):
    """Extracts the product name from the sub-link
    E.g. https://www.myer.com.au/p/tommy-hilfiger-essential-cotton-te-835469290-1:
        Returns:
            tommy-hilfiger-essential-cotton-te-835469290-1
    """
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