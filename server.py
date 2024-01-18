from flask import Flask, render_template, request
from threading import Thread
from googlesearch import search
from google_product_extractor import run
import asyncio
from fuzzywuzzy import fuzz
from price_finder import process_url
from image_finder import find_product_image

app = Flask(__name__)
'''
    user_input: Gets the input from the search bar and process it to be displayed to python
'''
def fuzzy_match(user_input, text):
    # Fuzzy string matching 
    return fuzz.partial_ratio(' '.join(user_input), text)

def run_scraping_task(query):
    asyncio.run(main(query))

@app.route('/search', methods=['POST'])
def searchItem():
    user_input = request.form['productName']
    print("User input:", user_input)

    query = user_input.split(' ')

    #Run scraping tasks in another fread
    scraping_thread = Thread(target=run_scraping_task, args=(query,))
    scraping_thread.start()
    return query


async def main(query):
    for url in search(' '.join(query), tld="co.in", num=10, stop=20, pause=0.1):
        if fuzzy_match(query, url) > 70:
            # print('awaiting.....')
            await process_url(url, query)

    # asyncio.run(main())
    # return search

@app.route('/')
def mockup():
    return render_template('mockup.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)