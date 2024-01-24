from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

async def find_product_description(link, session):
    async with session.get(link) as response:
        # Ensure that the response status is OK
        if response.status == 200:
            # Read the HTML content from the response
            html = await response.text()

            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(html, 'lxml')

            # Find all span tags with "description" in their text
            span_elements = soup.find_all('span', text=lambda text: text is not None and fuzz.partial_ratio("description", text.lower()))

            for s in span_elements:
                # Get the text content of the span
                text_content = s.text

                if text_content:
                    span_elements = soup.find_all('span', text=lambda text: text and "description" in text.lower())
                    list_element = await find_list_element_after_description(s)
                    if list_element:
                        print(f"Found List: {list_element.text}")
                        return text_content, list_element.text

    return "N/A"


async def find_list_element_after_description(matched_span):
    # Get the parent of the matched span
    parent_tag = matched_span.find_parent()

    # Find the next sibling
    next_sibling = parent_tag.find_next_sibling()

    # Look for a list in the next siblings
    while next_sibling:
        if await is_ul_or_li_element(next_sibling):
            return next_sibling
        next_sibling = next_sibling.find_next_sibling()

    return None

async def is_ul_or_li_element(tag):
    return tag.name == 'ul' or tag.name == 'li'