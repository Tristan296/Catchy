import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import spacy
from spacy.training.example import Example
from fuzzywuzzy import fuzz

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_product_name_from_href(url):
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


def scrape_prices(url, product_query):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'lxml')
        all_text = soup.get_text()

        # Preprocess the text to replace non-breaking space with a regular space
        all_text = all_text.replace('\xa0', ' ')

        # Extract product names using fuzzy matching
        product_names = set()

        # Extract prices using SpaCy NER
        prices = set()
        doc = nlp(all_text)

        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                prices.add(ent.text)

            if ent.label_ == 'PRODUCT':
                product_names.add(ent.text)

        # Extract links using fuzzy matching
        links = set()
        similar_names = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')

            links.add(href)

            # Extract the product name from the end of the URL
            product_name_from_href = extract_product_name_from_href(href)

            # Iterate through the NLP's found names and check for similarity with the href name
            for name in product_names:
                if fuzz.partial_ratio(name, product_name_from_href)> 50:
                    print("Name from NLP:", name)
                    print("Product name from link: ", product_name_from_href)
                    similar_names.add(name)

                # product_names.add((ent.text, product_name_from_href))

        print(similar_names)
        return prices, similar_names, links
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return set(), set(), set()
    
def search_products(url, product_query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}

    # Fetch the HTML content of the page
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')

        # Perform fuzzy matching with the product query
        similarity_threshold = 60
        matches = []
        for tag in soup.find_all(lambda tag: product_query.lower() in tag.text.lower()):
            similarity_ratio = fuzz.ratio(tag.text.lower(), product_query.lower())
            if similarity_ratio > similarity_threshold:
                matches.append(tag)

        # Extract links and entities for matched products
        for match in matches:
            product_name = match.text.strip()

            # Find the parent <a> tag
            parent_a_tag = match.find_parent('a')

            if parent_a_tag:
                # Get the 'href' attribute of the parent <a> tag
                href = parent_a_tag.get('href')

                if href:
                    # Add the joined URL to the 'links' set
                    product_link = urljoin(url, href)
                    print(f"Link: {product_link}")

                    # Extract product name and price using the scrape_prices function
                    prices, names, links = scrape_prices(product_link, product_query)
                    print(f"Product Name: {names}")
                    print(f"Prices: {prices}")

        print(f"Search completed for '{product_query}'.")

    else:
        print(f"Failed to retrieve data. Status Code: {r.status_code}")


if __name__ == "__main__":
    product_query = input("Enter product name: ")
    website_url = f"https://www.rebelsport.com.au/search?q={product_query}&lang=en_AU"

    search_products(website_url, product_query)
