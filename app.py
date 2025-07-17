from flask import Flask, request, jsonify,render_template
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF

app= Flask(__name__)
load_dotenv()

apikey='value'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        # Here you would typically process the user input and generate a response
        response = f"You said: {user_input}"
        return jsonify({'response': response})
    return render_template('index.html')