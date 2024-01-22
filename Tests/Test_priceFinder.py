import os
import sys
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup, Tag
from fuzzywuzzy import fuzz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

class PriceScraper:
    def __init__(self, link, soup, name):
        self.link = link
        self.soup = soup
        self.name = name

    async def find_product_info(self, product_name):
        if not isinstance(self.link, str):
            print("Skipping processing for link, it's not a string:", self.link)
            return None, None

        # Find all text-containing tags
        text_tags = [tag for tag in self.soup.find_all(lambda tag: tag.get_text())]

        # Find the tag with the highest fuzzy matching ratio to the link
        matched_tag = max(text_tags, key=lambda tag: fuzz.partial_ratio(self.name.lower(), tag.get_text().lower()))

        # Extract product information (name, price, etc.) from the matched tag
        product_info = await self.extract_product_info(matched_tag, product_name)

        if product_info:
            return product_info
        else:
            print("No product information found on the website.")
            return None

    async def extract_product_info(self, tag, product_name):
        # Placeholder function for extracting product information from a tag
        # You can customize this based on the structure of the HTML on the website
        name, product_name_element = self.extract_product_name_element(tag, product_name)

        price = await self.find_product_price(tag)

        return {
            "product_name": product_name,
            "product_name_element": product_name_element,
            "price": price,
            # Add more fields as needed
        }

    async def find_product_price(self, matched_tag):
        current_tag = matched_tag

        while current_tag:
            next_sibling = current_tag.findNext('div')

            if next_sibling:
                innermost_child = next_sibling.find(lambda tag: not tag.find_all(), recursive=False)

                if innermost_child:
                    # Use the text of the innermost_child tag as the price text
                    price_text = innermost_child.get_text(strip=True)

                    print("Price text: ", price_text)
                    if self.is_valid_price(price_text):
                        return price_text, innermost_child

            current_tag = next_sibling

        return None, None
    
    def extract_product_name_element(self, tag, product_name):
        # Check if the tag is a BeautifulSoup tag
        if isinstance(tag, Tag):
            tag_html = str(tag)
        else:
            tag_html = tag

        product_name_regex = re.escape(product_name)

        # Construct the regex pattern to include the product name within any parent tags
        pattern = re.compile(rf'(<[^>]*>{product_name_regex}<[^>]*>)', re.IGNORECASE | re.DOTALL)

        # Check if the product name is present in the matched content
        match = pattern.search(tag_html)

        if match:
            # Extract the matched portion
            matched_html = match.group()

            # Parse the matched HTML as a BeautifulSoup tag
            matched_tag = BeautifulSoup(matched_html, 'html.parser').find()

            return matched_tag.text, matched_tag

        return None, None
    
    def is_valid_price(self, text):
        # Use a regular expression to check if the text matches a typical price pattern
        price_pattern = re.compile(r'^\$\d+(\.\d{1,2})?$')  # Assumes a simple dollar amount (e.g., $10 or $10.50)
        return bool(price_pattern.match(text))


# Example usage:
async def main():
    name = "stainless steel mug"
    link = "https://www.amazon.com.au/Zojirushi-SM-KHE48BA-Stainless-Steel-Mug/dp/B00CHOUI86/?_encoding=UTF8&pd_rd_w=fOizi&content-id=amzn1.sym.619b3dc6-ef3f-4bd9-9bfc-7cf802ed96b7%3Aamzn1.symc.0245f497-9af2-4398-a94a-83302d9615b8&pf_rd_p=619b3dc6-ef3f-4bd9-9bfc-7cf802ed96b7&pf_rd_r=E0A8RWCGQTE1K748B7JN&pd_rd_wg=YKBmJ&pd_rd_r=0025f614-ca87-41a0-85b1-e1ebecdd9b43&ref_=pd_gw_ci_mcx_mr_hp_atf_m"
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')

                scraper = PriceScraper(link, soup, name)
                product_info = await scraper.find_product_info(name)

                price = await scraper.find_product_price(product_info['product_name_element'])
                print(price)
                
                if product_info:
                    print("Product Information:")
                    print(f"Product Name: {product_info['product_name']}")
                    print(f"Product Name Element: {product_info['product_name_element']}")
                    print(f"Price: {product_info['price']}")

                    # Print additional fields if needed


if __name__ == "__main__":
    asyncio.run(main())
