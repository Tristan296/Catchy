import os
from threading import Thread
from flask import Flask, render_template, request, jsonify
from googlesearch import search
import asyncio
from fuzzywuzzy import fuzz
from backend.webScraper import WebCrawler
from flask_cors import CORS
from flask_socketio import SocketIO
from gevent import monkey

monkey.patch_all()
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

    for url in search(' '.join(query), num=10, stop=20, pause=0.1):
        if fuzzy_match(query, url) > 70:
            crawler = WebCrawler(proxy_list=['https://198.176.56.39:80', 
                                            'http://62.210.114.201:8080', 
                                            'http://103.168.155.116:80', 
                                            'http://5.161.82.64:5654', 
                                            "http://191.101.80.162:80",
                                            "http://195.35.3.117:80", 
                                            "http://116.203.28.43:80", 
                                            "http://72.10.160.93:25873", 
                                            "http://165.22.36.164:10001",
                                            "http://47.254.91.248:3773",
                                            "http://178.159.39.153:8118",
                                            "http://67.43.227.228:9039",
                                            "http://102.130.125.86:80",
                                            "http://50.172.39.98:80",
                                            "http://50.168.210.238:80",
                                            "http://66.191.31.158:80",
                                            "http://50.168.210.226:80",
                                            "http://50.170.90.29:80",
                                            "http://138.201.51.183:9099",
                                            "http://78.28.152.78:80",
                                            "http://221.151.181.101:8000",
                                            "http://109.111.137.135:53281",
                                            "http://13.81.217.201:80",
                                            "http://50.169.23.170:80",
                                            "http://50.168.210.234:80"])
            
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
