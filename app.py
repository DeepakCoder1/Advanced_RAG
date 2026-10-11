from flask import Flask, render_template, request
from pdf_reader import extract_text_from_pdf
from  rag import add_document, generate_answer, collection
import os

app = Flask(__name__)


UPLOAD_FOLDER = 'documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route(
    "/upload",
    methods=["POST"]
)
def upload_pdf():

    if "pdf" not in request.files:

        return render_template(
            "index.html",
            error="Please select a PDF."
        )

    file = request.files["pdf"]


    if file.filename == "":

        return render_template(
            "index.html",
            error="Please select a PDF."
        )


    if not file.filename.lower().endswith(".pdf"):

        return render_template(
            "index.html",
            error="Only PDF files are allowed."
        )


    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )


    file.save(file_path)


    

    text = extract_text_from_pdf(
        file_path
    )



    chunk_count = add_document(
        text,
        file.filename
    )


    return render_template(
        "index.html",
        success=(
            f"{file.filename} uploaded successfully. "
            f"{chunk_count} chunks stored in ChromaDB."
        )
    )


@app.route(
    "/ask",
    methods=["POST"]
)
def ask_question():

    question = request.form.get(
        "question"
    )


    if not question:

        return render_template(
            "index.html",
            error="Please enter a question."
        )


    result = generate_answer(
        question
    )


    answer = result[0]

    sources = result[1]


    return render_template(
        "index.html",
        question=question,
        answer=answer,
        sources=sources
    )

if __name__ == "__main__":

    app.run(
        debug=True
    )


