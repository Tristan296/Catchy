from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import pandas as pd
import requests
import spacy
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags

from fuzzywuzzy import fuzz

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Annotated examples
TRAIN_DATA = [
    ("Add Sony X-Series Portable Wireless Speaker SRSXE300H in Grey to wishlist$319.00$249.00", {"entities": [(4, 61, "ORG"), (76, 81, "MONEY")]}),
    ("Add Sony X-Series Portable Wireless Speaker SRSXE300B in Black to wishlist$319.00$249.00", {"entities": [(4, 61, "ORG"), (76, 81, "MONEY")]}),
    ("Add Sony X-Series Portable Wireless Speaker SRSXE200H in Grey to wishlist$249.00$189.00", {"entities": [(4, 60, "ORG"), (75, 80, "MONEY"),]}),
    ("Add Sony X-Series Portable Wireless Speaker SRSXE200L in Blue to wishlist$249.00$189.00", {"entities": [(4, 60, "ORG"), (74, 79, "MONEY"),]}),
    ("Add Sony X-Series Portable Wireless Speaker SRSXG300B in Black to wishlist$479.00$383.20", {"entities": [(4, 61, "ORG"), (74, 79, "MONEY")]}),
    ("Add Sony X-Series Portable Wireless Speaker SRSXG300H in Grey to wishlist$479.00$383.20", {"entities": [(4, 60, "ORG"), (74, 79, "MONEY"),]}),
    ("Add Sony Linkbuds S WFLS900NB in Black to wishlist$349.95$279.96", {"entities": [(4, 38, "ORG"), (67, 72, "MONEY")]}),
    ("Add Sony Sony Black On Ear Noise Cancelling Headphones MDRZX110NC to wishlist$99.95$79.95", {"entities": [(4, 65, "ORG"), (92, 97, "MONEY")]}),
    ("Core Cargo Shorts in Dress Beige Add Superdry", {"entities" : [(0, 32, "ORG")]})
]

# Train the model
for epoch in range(10):
    for example in TRAIN_DATA:
        text, gold_dict = example
        example = Example.from_dict(nlp.make_doc(text), gold_dict)
        nlp.update([example], drop=0.5)

print(nlp.tokenizer.explain(text))

def scrape_prices(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses
        soup = BeautifulSoup(response.content, 'lxml')
        all_text = soup.get_text()

        # Preprocess the text to replace non-breaking space with a regular space
        all_text = all_text.replace('\xa0', ' ')

        price_patterns = re.findall(r'\$\s?\d+(?:,\d+)*(?:\.\d+)?', all_text)
        
        prices = set()
        links = set()
        names = set()

        for pattern in price_patterns:
            doc = nlp(pattern)
            for ent in doc.ents:
                if ent.label_ == 'MONEY':
                    prices.add(ent.text)

        doc = nlp(all_text)
        for ent in doc.ents:
            if ent.label_ == 'ORG' :
                names.add(ent.text)
                text = ent.text.replace(' ', '-')
                # Find all <a> tags in the soup
                all_a_tags = soup.find_all('a')

                # Iterate through each <a> tag
                for a_tag in all_a_tags:
                    # Get the 'href' attribute of the current <a> tag
                    href = a_tag.get('href')

                    # Check if 'href' is not None and if the partial ratio is above a certain threshold (e.g., 70)
                    if href and fuzz.partial_ratio(text, href) > 70:
                        # Add the joined URL to the 'links' set
                        links.add(urljoin("https://www.myer.com.au/", href))

        return prices, names, links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return set(), set(), set()

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

url = 'https://www.myer.com.au/c/men/mens-clothing/mens-shorts'
prices_df = analyze_prices(url)
print(prices_df)


for text, annotations in TRAIN_DATA:
    doc = nlp.make_doc(text)
    tags = offsets_to_biluo_tags(doc, annotations["entities"])
    print(f"Text: {text}")
    print(f"Tags: {tags}")

