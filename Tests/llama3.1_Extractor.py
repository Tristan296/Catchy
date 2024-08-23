from bs4 import BeautifulSoup
import requests
from groq import Groq
import html2text

client = Groq(api_key="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")

# Get the product details from the website
def get_product_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    text_content = html2text.html2text(response.text)
    text_content = text_content.strip()

    return text_content

# Get the product details from the website
soup = get_product_details('https://www.myer.com.au/c/men/featured-menswear-brands/calvin-klein-1') 

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f'''
            Please extract the following information from the provided HTML content, ignoring any JavaScript and non-relevant elements:
            1. Product names.
            2. Product prices.
            3. Product descriptions.
            
            Focus only on extracting text data related to products and ignore any script tags, inline JavaScript, or external library references.

            HTML content:

            {soup}
            ''',
        }
    ],
    model="llama-3.1-8b-instant",
)
print(chat_completion.choices[0].message.content)
