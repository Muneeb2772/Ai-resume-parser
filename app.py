from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
from llama_integration import extract_name_email_with_llama
import fitz  # PyMuPDF for PDF extraction
from docx import Document  # python-docx for DOCX extraction

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['CSV_FOLDER'] = './csv_files/'  # Folder to save CSV files

# Ensure the CSV folder exists
os.makedirs(app.config['CSV_FOLDER'], exist_ok=True)

def extract_text_from_pdf(file_path):
    text = ''
    pdf_document = fitz.open(file_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    data = []

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from the resume file (PDF/DOCX logic here)
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            continue  # Unsupported file type

        # Use LLaMA model to extract name and email
        name, email = extract_name_email_with_llama(text)
        data.append({'Filename': filename, 'Name': name, 'Email': email})

    # Create DataFrame and save as CSV
    df = pd.DataFrame(data)
    csv_file_path = os.path.join(app.config['CSV_FOLDER'], 'output.csv')
    df.to_csv(csv_file_path, index=False)

    # Render results page with data and download link
    return render_template(
        'result.html',
        tables=[df.to_html(classes='table table-striped', header="true")],
        csv_file='output.csv'
    )

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CSV_FOLDER'], filename, as_attachment=True)
