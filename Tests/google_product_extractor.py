import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tldextract

def extract_sublinks_with_substring(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'lxml')

        # Find all anchor tags with 'href' attribute
        anchor_tags = soup.find_all('a', href=True)

        # Extract information from URL
        extracted_info = tldextract.extract(url)

        allowed_substring = get_allowed_substring(extracted_info.domain)

        # Extract sublinks with  allowed substring in the URL
        sublinks = [urljoin(url, a['href']) for a in anchor_tags if allowed_substring in a['href']]

        return sublinks

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
    

def get_allowed_substring(website_name):
    """
    This method defines a dictionary that has each website assigned to its own allowed substring.
    This substring serves as a filter to selectively extract product links.

    E.g. JBHIFI -> '/products/'
         MYER -> '/p/'
         OFFICEWORKS -> '/shop/'

    Returns:
        Substring (str)
    """
    allowed_substrings = {
        "jbhifi": '/products/',
        "myer": '/p/',
        "rebelsport": '/p/',
        "nike": '/t/',
        "officeworks": '/shop/officeworks/',
        "jd-sports": '/product/',
        "davidjones": '/product/',
        "binglee": '/products/',
        "puma": '/pd/',
        "asics": '/en/au/'
    }

    website_name = website_name or "default"
    substring = allowed_substrings.get(website_name, "default")

    return substring


def run(url, product_name):
    print(f"Scraping {url} for products...")
    sublinks = extract_sublinks_with_substring(url)
    # Display the extracted sublinks

    for sublink in sublinks:
        print(sublink)
    print("---" * 20)
