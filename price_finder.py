import aiohttp
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urlparse
import tldextract
import yarl
from image_finder import find_product_image
import re 
from fuzzywuzzy import fuzz
from price_finder_old import find_product_name_element


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
        "binglee": '/products/',
        "jd-sports": '/product/',
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

    # Extract the keyword from the hostname:
    #Example: https://www.myer.com.au/p/health.......
    #Will get "myer"
    keyword = parsed_url.hostname.split('.')[1]

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

    # website_name = website_name or "default"
    # substring = allowed_substrings.get(website_name, "default")
    # print(f"substring allowed for {website_name} is {substring}.")
    # return substring

    if getTag in allowed_substrings.values():
        # substring = allowed_substrings.get(website_name, "default")
        print(f"substring allowed for {website_name} is {getTag}.")
        setFlag = True
        return setFlag
    else:
        setFlag = False
        print(f"substring {getTag} not defined for {keyword}.")
        return setFlag


async def process_url(url, setFlag, product_name, processed_sublinks=set(), printed_prices=set()):
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
        soup = BeautifulSoup(html_content, 'lxml', parse_only=SoupStrainer('a'))
        url_info = tldextract.extract(url)

        # allowed_substring = await get_allowed_substring(url_info.domain, product_name)

        await process_sub_url(url, soup, session, processed_sublinks, f"https://www.{url_info.domain}.com.au/", product_name, setFlag)


async def process_sub_url(url, soup, session, processed_sublinks, base_url, product_name, setFlag):
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
 
    sublinks = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if fuzz.partial_ratio(product_name, yarl.URL(a['href']).path.replace('/', '-')) > 40}
    
    # Process only new sublinks
    new_sublinks = sublinks - processed_sublinks

    for sublink in new_sublinks:
        # gets tags for sublinks (returns links that link towards the product)
        sublink_tags = await get_allowed_substring(sublink, sublink, setFlag)
        
        if sublink and sublink_tags ==True:
        # if sublink:
            sublink_response = await session.get(sublink)
            sublink_html_content = await sublink_response.text()
            sublink_soup = BeautifulSoup(sublink_html_content, 'lxml')
            sublink_text_content = sublink_soup.get_text()

            # gets prices for sublinks (returns array of prices)
            sublink_price, innermost_price_element = await find_product_name_element(sublink, sublink_soup)
            
            print('sublink tags:', sublink_tags)
            if sublink_price:
                print("Found Product details:")
                print(f"Link: {sublink}")
                print(f"Price: {sublink_price}\n\n")


    # Add processed sublinks to the set
    processed_sublinks.update(new_sublinks)

