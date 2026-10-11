import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

embedding_model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"

)

collection = chroma_client.get_or_create_collection(
    name='pdf_documents'
)

def create_chunk(text, chunk_size=800):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(
            words[i:i + chunk_size]
        )
        chunks.append(chunk)

    return chunks

def add_document(text, filename):
    chunks = create_chunk(text)

    if not chunks:
        return 0
    embeddings = embedding_model.encode(chunks).tolist()
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(
            f"{filename}_{i}"

        )
        documents.append(chunk)
        metadatas.append(
            {
                "filename": filename,
                "chunk_id": i
            }
        )
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(chunks)


def search_documents(question, top_k=5):
    questions_embeddings = embedding_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[questions_embeddings],
        n_results=top_k
    )
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    return documents, metadatas

def generate_answer(question):

    documents, metadatas = search_documents(
        question
    )

    if not documents:

        return "I could not find relevant information in the documents."

    context = "\n\n".join(
        documents
    )

    prompt = f"""
You are a helpful document assistant.

Answer the user's question using ONLY the
information provided in the context.

If the answer is not available in the context,
say:

"I could not find the answer in the uploaded documents."

Do not make up information.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": "You answer questions from provided documents."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    answer = response.choices[0].message.content

    sources = []

    for metadata in metadatas:

        sources.append(
            {
                "filename": metadata["filename"],
                "chunk_id": metadata["chunk_id"]
            }
        )

    return answer, sources
