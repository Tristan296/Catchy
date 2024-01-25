from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import pandas as pd
import requests
import spacy
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Annotated examples
TRAIN_DATA = [
     ("Add MADDOX Mason Geo Print Short Sleeve Shirt in Navy to wishlist$69.95$41.97", {"entities": [(4, 53, "PRODUCT"), (65, 76, "MONEY")]}),
     ("X-Series Portable Wireless Speaker SRSXE300H in Grey to wishlist$319.00$249.00", {"entities": [(0, 56, "PRODUCT"), (81, 87, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXE300H in Grey to wishlist$319.00$249.00", {"entities": [(0, 56, "PRODUCT"), (75, 80, "MONEY"), (81, 87, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXE300B in Black to wishlist$319.00$249.00", {"entities": [(0, 56, "PRODUCT"), (75, 80, "MONEY"), (81, 87, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXE200H in Grey to wishlist$249.00$189.00", {"entities": [(0, 55, "PRODUCT"), (74, 79, "MONEY"), (80, 86, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXE200L in Blue to wishlist$249.00$189.00", {"entities": [(0, 54, "PRODUCT"), (73, 78, "MONEY"), (79, 85, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXG300B in Black to wishlist$479.00$383.20", {"entities": [(0, 54, "PRODUCT"), (73, 78, "MONEY"), (79, 85, "MONEY")]}),
    ("Sony X-Series Portable Wireless Speaker SRSXG300H in Grey to wishlist$479.00$383.20", {"entities": [(0, 54, "PRODUCT"), (73, 78, "MONEY"), (79, 85, "MONEY")]}),
    ("Sony Linkbuds S WFLS900NB in Black to wishlist$349.95$279.96", {"entities": [(0, 47, "PRODUCT"), (66, 71, "MONEY"), (72, 78, "MONEY")]}),
    ("Sony Sony Black On Ear Noise Cancelling Headphones MDRZX110NC to wishlist$99.95$79.95", {"entities": [(0, 72, "PRODUCT"), (91, 96, "MONEY"), (97, 103, "MONEY")]}),
    ("Sony Black In Ear Headphones MDREX15AP to wishlist$29.95$19.95", {"entities": [(0, 46, "PRODUCT"), (65, 70, "MONEY"), (71, 77, "MONEY")]}),
    ("Sony White In Ear Headphones MDREX155AP to wishlist$54.95$32.97", {"entities": [(0, 47, "PRODUCT"), (66, 71, "MONEY"), (72, 78, "MONEY")]}),
    ("Sony Black In Ear Headphones MDRE9LPB to wishlist$14.95$9.95", {"entities": [(0, 47, "PRODUCT"), (66, 71, "MONEY"), (72, 78, "MONEY")]}),
    ("Sony Blue In Ear Headphones MDREX15AP to wishlist$29.95$19.95", {"entities": [(0, 46, "PRODUCT"), (65, 70, "MONEY"), (71, 77, "MONEY")]}),
    ("Sony White In Ear Headphones MDRE9LPW to wishlist$14.95$9.95", {"entities": [(0, 47, "PRODUCT"), (66, 71, "MONEY"), (72, 78, "MONEY")]}),
    ("Sony Blue In Ear Headphones MDRE9LPL to wishlist$14.95$9.95", {"entities": [(0, 46, "PRODUCT"), (65, 70, "MONEY"), (71, 77, "MONEY")]}),
    ("Sony Wireless headphones Black WHCH520B to wishlist$99.95$79.95", {"entities": [(0, 51, "PRODUCT"), (70, 75, "MONEY"), (76, 82, "MONEY")]}),
    ("Sony Black Noise Cancelling Headphones WH1000XM4B to wishlist$549.00$439.00", {"entities": [(0, 55, "PRODUCT"), (74, 79, "MONEY"), (80, 86, "MONEY")]}),
]

# Train the model
for epoch in range(10):
    for example in TRAIN_DATA:
        text, gold_dict = example
        example = Example.from_dict(nlp.make_doc(text), gold_dict)
        nlp.update([example], drop=0.5)

def scrape_prices(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all text on the page
    all_text = soup.get_text()

    # Use regular expression to find potential price patterns
    price_patterns = re.findall(r'\$\s?\d+(?:,\d+)*(?:\.\d+)?', all_text)

    # Process the text using spaCy to filter out non-price entities
    prices = []
    links = []
    names = []
    for pattern in price_patterns:
        doc = nlp(pattern)
        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                prices.append(ent.text)

    doc = nlp(all_text)
    for ent in doc.ents:
        if ent.label_ == 'PRODUCT':
            names.append(ent.text)
            # Check if there is a link with the product name
            text = ent.text.replace(' ', '-')
            link = soup.find('a', {'href': re.compile(fr'{re.escape(text)}', re.I)})
            links.append(urljoin(url, link.get('href')) if link else None)

    return prices, names, links

def prices_to_dataframe(names, prices, links):
    # Create a DataFrame with 'name' and 'price' columns
    df = pd.DataFrame(list(zip(names, prices,links)), columns=['price', 'name', 'link'])
    # Save DataFrame to a CSV file
    df.to_csv('output.csv', index=False)
    return df

def analyze_prices(url):
    prices, names, links= scrape_prices(url)
    prices_df = prices_to_dataframe(prices,names,links)
    return prices_df

url = 'https://www.myer.com.au/b/Sony'
prices_df = analyze_prices(url)
print(prices_df)
