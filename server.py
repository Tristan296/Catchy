from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search():
    user_input = request.form['productName']
    # Do something with the user_input (e.g., print it)
    print("User input:", user_input)
    return user_input

@app.route('/')
def mockup():
    return render_template('mockup.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)