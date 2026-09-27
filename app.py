from flask import Flask, render_template, request
from pdf_reader import extract_text_from_pdf
import os

app = Flask(__name__)


UPLOAD_FOLDER = 'documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return 'No pdf file selected'
    file = request.files['pdf']

    if file.filename == "":
        return 'please select a pdf file'

    if not file.filename.lower().endswith(".pdf"):
        return "only pdf file are allowed"

    file_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file.filename
    )
    file.save(file_path)
    text = extract_text_from_pdf(file_path)



    return render_template('index.html', text=text, filename=file.filename)



if __name__ == "__main__":

    app.run(
        debug=True
    )


