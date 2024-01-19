from bs4 import BeautifulSoup
import pytest
import asyncio
from aioresponses import aioresponses
from ..backend.priceFinder import PriceScraper
from html_content import REAL_HTML_CONTENT

@pytest.fixture
def mock_link():
    # Replace 'YourMockLink' with the actual link you want to test
    return 'https://example.com/link1'  # Choose a link from REAL_HTML_CONTENT

@pytest.fixture
async def mock_soup(mock_link):
    # You can use your actual scraping logic here to create a BeautifulSoup object from the real HTML content
    # For this example, we'll use a simple mock
    html_content = REAL_HTML_CONTENT.get(mock_link, "")
    return BeautifulSoup(html_content, 'html.parser')

@pytest.fixture
def price_scraper_instance(mock_link, mock_soup):
    return PriceScraper(mock_link, mock_soup)

@pytest.mark.asyncio
async def test_find_product_name_element(mock_link, mock_soup, price_scraper_instance):
    # Your test logic here
    with aioresponses() as m:
        # Mock the HTTP response for the provided link using real HTML content
        m.get(mock_link, body=REAL_HTML_CONTENT.get(mock_link, ""))

        price, innermost_child = await price_scraper_instance.find_product_name_element()
        
        # Assert statements based on expected results
        assert price is not None
        assert innermost_child is not None