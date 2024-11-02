import os
import time
import boto3
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from transformers import BartForConditionalGeneration, BartTokenizer
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from fastapi.responses import JSONResponse

#Load environment variables
load_dotenv()

#AWS S3 credentials
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
BUCKET_NAME = "bigdata-team9"
S3_FOLDER_PATH = "scraped_raw/pdfs/"

#Initialize FastAPI app
app = FastAPI()

#Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

#Load the NVIDIA API key
os.environ['NVIDIA_API_KEY'] = ""

# Function to list PDF files in the specified S3 folder
def list_pdfs_from_s3(bucket, folder_path):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder_path)
    pdf_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]
    return pdf_files

# Function for embedding selected document
def vector_embedding(selected_pdf_key):
    vectors = None
    loader = None
    docs = None
    embeddings = None
    text_splitter = None
    final_documents = None

    start_time = time.time()  # Start timing the embedding process

    embeddings = NVIDIAEmbeddings()
    
    # Download the selected PDF from S3
    selected_pdf_path = "/tmp/selected_pdf.pdf"
    s3_client.download_file(BUCKET_NAME, selected_pdf_key, selected_pdf_path)
    
    # Load the downloaded PDF document
    loader = PyPDFLoader(selected_pdf_path)
    docs = loader.load()

    # Split documents into chunks for embedding
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
    final_documents = text_splitter.split_documents(docs)

    # Generate vector embeddings
    vectors = FAISS.from_documents(final_documents, embeddings)

    # Display embedding time
    end_time = time.time()
    embedding_time = end_time - start_time
    return vectors, embedding_time

# Save response to research notes with status (Correct/Incorrect)
def save_research_note_response(question, response, status):
    with open("research_notes.txt", "a") as file:
        file.write(f"Question: {question}\n")
        file.write(f"Response: {response}\n")
        file.write(f"Status: {status}\n")
        file.write("--------\n")

# Function to generate summary using the BART model
def generate_summary(text):
    model_name = 'facebook/bart-large-cnn'
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        max_length=15000,
        min_length=300,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    if len(summary) > 10000:
        summary = summary[:10000] + '... [Truncated]'

    return summary

@app.get("/")
def read_root():
    return HTMLResponse("""
    <html>
        <head>
            <title>Document Interaction App</title>
        </head>
        <body>
            <h1>Welcome to the Document Interaction App</h1>
            <p>Use the endpoints to interact with PDFs and generate summaries.</p>
        </body>
    </html>
    """)

@app.get("/list_pdfs")
def list_pdfs():
    try:
        pdf_files = list_pdfs_from_s3(BUCKET_NAME, S3_FOLDER_PATH)
        return JSONResponse(content={"pdf_files": pdf_files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_summary/")
def generate_pdf_summary(selected_pdf: str):
    try:
        selected_pdf_path = "/tmp/selected_pdf.pdf"
        s3_client.download_file(BUCKET_NAME, selected_pdf, selected_pdf_path)

        loader = PyPDFLoader(selected_pdf_path)
        docs = loader.load()
        full_text = "\n".join([doc.page_content for doc in docs])

        summary = generate_summary(full_text)
        return JSONResponse(content={"summary": summary})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vector_embedding/")
def embed_document(selected_pdf: str):
    try:
        vectors, embedding_time = vector_embedding(selected_pdf)
        return JSONResponse(content={"message": "Vector Store DB Is Ready", "embedding_time": embedding_time})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer_question/")
def answer_question(selected_pdf: str, question: str):
    try:
        vectors, _ = vector_embedding(selected_pdf)
        llm = ChatNVIDIA(model="meta/llama-3.1-405b-instruct")
        prompt = ChatPromptTemplate.from_template(
            """
            Answer the questions based on the provided context only.
            Please provide the most accurate response based on the question
            <context>
            {context}
            <context>
            Questions: {input}
            """
        )

        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.process_time()
        response = retrieval_chain.invoke({'input': question})
        elapsed_time = time.process_time() - start

        save_research_note_response(question, response['answer'], "Pending")

        return JSONResponse(content={"answer": response['answer'], "response_time": elapsed_time})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/")
def get_report():
    correct_count = 0
    incorrect_count = 0

    if os.path.exists("research_notes.txt"):
        with open("research_notes.txt", "r") as file:
            for line in file:
                if "Status: Correct" in line:
                    correct_count += 1
                elif "Status: Incorrect" in line:
                    incorrect_count += 1

    total = correct_count + incorrect_count
    accuracy = (correct_count / total * 100) if total > 0 else 0

    data = {
        'Total Questions': total,
        'Correct Answers': correct_count,
        'Incorrect Answers': incorrect_count,
        'Overall Accuracy (%)': accuracy
    }
    return JSONResponse(content=data)

# Ensure the static directory exists before mounting
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")
