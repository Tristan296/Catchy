import asyncio
import io
import re
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fuzzywuzzy import fuzz
import requests
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import numpy as np

async def find_product_image(link, session, base_url):
    async with session.get(link) as response:
        # Ensure that the response status is OK
        if response.status == 200:
            # Read the HTML content from the response
            html = await response.text()

            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(html, 'lxml')

            # Get the product name
            product_name = await extract_product_name(link)

            # Find all img tags
            images = soup.find_all('img')

            for image in images:
                # Get the src and alt attributes
                src_value = image.get('src') or image.get('data-src')
                alt = image.get('alt', '').lower()

                # Use fuzzy matching for alt attribute
                ratio = fuzz.ratio(product_name, alt)

                if ratio > 40:
                    # Classify the image using MobileNetV2
                    predictions = await classify_image(src_value, base_url)

                    #Join the base url with the found image url
                    src_value = urljoin(base_url, src_value)
                    
                    # Display the top prediction
                    if predictions:
                        top_prediction = predictions[0]
                        print(f"Found image with matching alt: {src_value}")
                        print(f"Top Prediction: {top_prediction[1]} ({top_prediction[2]:.2f})")

                    return src_value, alt

    return None, None

async def extract_product_name(url):
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

async def classify_image(image_url, base_url):
    try:
        # Load MobileNetV2 model
        model = MobileNetV2(weights='imagenet')

        # Load and preprocess the image from the URL
        img_data = requests.get(image_url).content
        img = image.img_to_array(image.load_img(io.BytesIO(img_data), target_size=(224, 224)))
        x = np.expand_dims(img, axis=0)
        x = preprocess_input(x)

        # Make predictions
        predictions = model.predict(x)
        decoded_predictions = decode_predictions(predictions, top=1)[0]

        return decoded_predictions

    except Exception as e:
        print(f"Error classifying image: {e}")
        return None
