import re
from yarl import URL
import asyncio 

def extract_product_name(url_parts):
    # Extract the product name from the second element onward in the path
    if url_parts:
        product_name = url_parts[1:]
        return product_name

    return ""  # Return an empty string if no product name is found

# Example usage:
urls = [
    'https://www.example.com/BUZIO-Stainless-Bottle-Vacuum-Insulated/dp/B07R3HYDVW/',
    'https://www.example.com/products/gymshark-legacy-oversized-t-shirt-white-ss22',
    'https://www.example.com/p/the-cooks-collective-triple-frypan-pack-w-silicone-handles'
]

url_parts_list = [URL(url).raw_parts for url in urls]
url_info = [extract_product_name(url_parts) for url_parts in url_parts_list]
print(url_info)