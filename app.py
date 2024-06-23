import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import json
import subprocess
import time

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder=os.path.join('UI', 'templates'), static_folder=os.path.join('UI', 'static'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_agent', methods=['POST'])
def add_agent():
    # Add your existing agent creation logic here
    return jsonify({"message": "Agent added successfully"}), 200

@app.route('/generate_output', methods=['POST'])
def generate_output():
    # Run the demo.py script to generate the PDF

    # Wait for 10 seconds to ensure the PDF is generated
    time.sleep(10)

    pdf_path = "output.pdf"
    return jsonify({"message": "PDF generated successfully", "pdf_url": f"/download/{pdf_path}"}), 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(debug=False)
