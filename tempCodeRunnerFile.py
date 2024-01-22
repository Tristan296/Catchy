#This gets data from userInput and sends it to priceFinder.py as input
@app.route('/search', methods=['POST'])
def searchItem():
    user_input = request.form['productName']
    print("User input:", user_input)

    query = user_input.split(' ')

    scraping_thread = Thread(target=run_scraping_task, args=(query,))
    scraping_thread.start()

    '''
        url_for: shows the path to flask method. Ours will be the method called "showResults()"
                 This will takes us to the 'scrapedLinks.html' page
    '''
    return redirect(url_for('showResults'))
    # return jsonify({"status": "success", "message": "Scraping task initiated."})


@app.route('/fetchData')
def fetchData():
    global global_products_data
    return jsonify({"status": "success", "products": global_products_data})

@app.route('/showResults', methods=['GET', 'POST'])
def showResults():
    global global_products_data
    send_message = 'hello'
    # return render_template('scrapedLinks.html', products=global_products_data)
    return render_template('scrapedLinks.html', products=send_message)

@app.route('/')
def mockup():
    return render_template('/mockup.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)