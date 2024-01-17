from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.form['user_input']
    # Do something with the user_input (e.g., print it)
    print("User input:", user_input)
    return "Input received successfully!"

@app.route('/')
def mockup():
    return render_template('mockup.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)