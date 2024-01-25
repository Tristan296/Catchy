from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

async def find_product_description(link, session, product_name):
    async with session.get(link) as response:
        # Ensure that the response status is OK
        if response.status == 200:
            # Read the HTML content from the response
            html = await response.text()

            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(html, 'lxml')

            # Find all span tags with "description" in their text
            span_elements = soup.find_all('span', text=lambda text: text is not None and fuzz.partial_ratio(r"(description|info)", text.lower()))

            for s in span_elements:
                # Get the text content of the span
                text_content = s.text

                if text_content:
                    list_element, innermost_child = await find_list_element_after_description(s, product_name)
                    if list_element:
                        print(f"Found List: {list_element}")
                        return text_content, list_element

    return "N/A"

async def find_list_element_after_description(matched_span, product_name):
    # Get the parent of the matched span
    parent_tag = matched_span.find_parent()

    # Find the next sibling
    next_sibling = parent_tag.find_next_sibling()

    # Look for a list in the next siblings
    while next_sibling:
        if next_sibling:
            innermost_child = next_sibling.find(lambda tag: not tag.find_all(), recursive=False)

            if innermost_child:
                price_text = innermost_child.text.strip()

                return price_text, innermost_child

        # Move to the next sibling
        next_sibling = next_sibling.find_next_sibling()

    return None, None