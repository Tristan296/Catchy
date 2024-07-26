import os, sys
from gevent import monkey

# Increase recursion limit
sys.setrecursionlimit(1500)
monkey.patch_all()


from threading import Thread
from flask import Flask, render_template, request, jsonify
from googlesearch import search
import asyncio
from fuzzywuzzy import fuzz
from backend.webScraper import WebCrawler
from flask_cors import CORS
from flask_socketio import SocketIO


app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, async_mode='gevent')

# Set the GEVENT_SUPPORT environment variable
os.environ['GEVENT_SUPPORT'] = 'True'

# Variable to store product data globally
global_products_data = []

def fuzzy_match(user_input, text):
    return fuzz.partial_ratio(' '.join(user_input), text)

async def main(query):
    setFlag = False
    products_data = []
    for url in search(' '.join(query), num_results=10, timeout=15):
        if fuzzy_match(query, url) > 70:
            crawler = WebCrawler()
            
            product_data = await crawler.process_url(url, setFlag, query, socketio)
            products_data.append(product_data)

def run_scraping_task(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main(query))
    finally:
        loop.close()

@app.route('/search', methods=['POST'])
def searchItem():
    user_input = request.form['productName']
    print("User input:", user_input)

    query = user_input.split(' ')

    # Start the scraping task in the background without displaying the message
    socketio.start_background_task(target=run_scraping_task, query=query)

    return jsonify({"status": "success"})

@app.route('/fetchData')
def fetchData():
    global global_products_data
    return jsonify({"status": "success", "products": global_products_data})

@app.route('/')
def mockup():
    return render_template('/mockup.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
