from urllib.parse import urlsplit, urljoin
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
import requests


def url_similarity(url1, url2):
    # Split URLs into components
    components1 = urlsplit(url1)
    components2 = urlsplit(url2)

    # Compare individual components using partial_ratio
    scheme_similarity = fuzz.partial_ratio(components1.scheme, components2.scheme)
    netloc_similarity = fuzz.partial_ratio(components1.netloc, components2.netloc)
    path_similarity = fuzz.partial_ratio(components1.path, components2.path)

    # Adjust these weights based on the importance of each component
    total_similarity = 0.4 * scheme_similarity + 0.4 * netloc_similarity + 0.2 * path_similarity
    
    return total_similarity

# Example usage
product_name = "keji a4"
url = "https://www.officeworks.com.au/shop/officeworks/p/keji-a4-button-document-wallet-blue-kebdocwabe"
url_response =  requests.get(url)
url_content = url_response.text
link_soup = BeautifulSoup(url_content, 'lxml')

sublinks = [urljoin(url, a['href']) for a in link_soup.find_all('a', href=True)]

similar_urls = [sublink for sublink in sublinks if url_similarity(product_name, sublink) > 40]

print(suilar)