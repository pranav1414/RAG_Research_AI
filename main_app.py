import streamlit as st
import os
import time
import boto3
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from transformers import BartForConditionalGeneration, BartTokenizer
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS

#Load environment variables
load_dotenv()

#S3 credentials
AWS_ACCESS_KEY_ID = "AKIATQZCSU4ZCFJ43IOM"
AWS_SECRET_ACCESS_KEY = "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"
BUCKET_NAME = "bigdata-team9"
S3_FOLDER_PATH = "scraped_raw/pdfs/"

#Initialize S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

#Function to list PDF files in the specified S3 folder
def list_pdfs_from_s3(bucket, folder_path):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder_path)
    pdf_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]
    return pdf_files


os.environ['NVIDIA_API_KEY'] = "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"

# Function for embedding
def vector_embedding(selected_pdf_key):
 # Reset the session state if a new PDF is selected
    st.session_state.vectors = None
    st.session_state.loader = None
    st.session_state.docs = None
    st.session_state.embeddings = None
    st.session_state.text_splitter = None
    st.session_state.final_documents = None
    
    start_time = time.time()  # Start timing the embedding process

    # Initialize embeddings and load the selected document from S3
    st.session_state.embeddings = NVIDIAEmbeddings()
    
    # Download the selected PDF from S3
    selected_pdf_path = "/tmp/selected_pdf.pdf"
    s3_client.download_file(BUCKET_NAME, selected_pdf_key, selected_pdf_path)
    
    # Load the downloaded PDF document
    st.session_state.loader = PyPDFLoader(selected_pdf_path)  # Load only the selected PDF
    st.session_state.docs = st.session_state.loader.load()  # Document Loading

    # Split documents into chunks for embedding
    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)

    # Generate vector embeddings
    st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

    # Display embedding time
    end_time = time.time()
    embedding_time = end_time - start_time
    st.write(f"Document Embedding Time: {embedding_time:.2f} seconds")

#Save response to research notes with status (Correct/Incorrect)
def save_research_note_response(question, response, status):
    with open("research_notes.txt", "a") as file:
        file.write(f"Question: {question}\n")
        file.write(f"Response: {response}\n")
        file.write(f"Status: {status}\n")
        file.write("--------\n")

#Function to generate summary using the BART model
def generate_summary(text):
    model_name = 'facebook/bart-large-cnn'
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    #Tokenize and generate summary
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

    #Limit summary to 10,000 characters
    if len(summary) > 10000:
        summary = summary[:10000] + '... [Truncated]'

    return summary

#Set up Streamlit app layout and navigation
st.set_page_config(layout="wide", page_title="Document Interaction App")
st.sidebar.title("LLM Tabs")

#Retrieve PDF files from S3
pdf_files = list_pdfs_from_s3(BUCKET_NAME, S3_FOLDER_PATH)

#Navigation tabs
tabs = ["Summary Generation", "Multimodal RAG", "Report"]
selected_tab = st.sidebar.selectbox("Select a tab:", tabs)

#Summary Generation Page
if selected_tab == "Summary Generation":
    st.title("PDF Summary")
    selected_pdf = st.selectbox("Select a PDF file:", pdf_files)
    if st.button("Load Summary"):
        st.write(f"Generating summary for {selected_pdf}...")

        # Download the selected PDF from S3
        selected_pdf_path = "/tmp/selected_pdf.pdf"
        s3_client.download_file(BUCKET_NAME, selected_pdf, selected_pdf_path)

        # Load the PDF document and extract text
        loader = PyPDFLoader(selected_pdf_path)
        docs = loader.load()
        full_text = "\n".join([doc.page_content for doc in docs])

        # Generate summary
        summary = generate_summary(full_text)
        st.write("### Summary:")
        st.write(summary)

#Multimodal RAG Page
elif selected_tab == "Multimodal RAG":
    st.title("Multimodal RAG: PDF Interaction (Q/A)")
    selected_pdf = st.selectbox("Select a PDF file:", pdf_files)

    #Document embedding button
    if st.button("Documents Embedding"):
        vector_embedding(selected_pdf)
        st.write("Vector Store DB Is Ready")

    #Prompt input for questions
    question = st.text_input("Enter Your Question From Documents")
    if question:
        # Set up NVIDIA LLM for Q/A
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

        # Retrieve and answer question based on document context
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.process_time()
        response = retrieval_chain.invoke({'input': question})
        elapsed_time = time.process_time() - start
        st.write(f"Response Time: {elapsed_time:.2f} seconds")

        # Display response
        st.subheader("Generated Answer")
        st.write(response['answer'])

        # Provide feedback buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Correct Answer"):
                save_research_note_response(question, response['answer'], "Correct")
                st.success("Marked as Correct")
        with col2:
            if st.button("Wrong Answer"):
                save_research_note_response(question, response['answer'], "Incorrect")
                st.warning("Marked as Incorrect")

        # Display document similarity search results
        with st.expander("Document Similarity Search"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------------------")

# Report Page
elif selected_tab == "Report":
    st.title("Report and Accuracy")
    st.write("Displaying the report and accuracy of answers from Multimodal RAG.")

    # Check if research notes file exists
    correct_count = 0
    incorrect_count = 0

    if os.path.exists("research_notes.txt"):
        with open("research_notes.txt", "r") as file:
            for line in file:
                if "Status: Correct" in line:
                    correct_count += 1
                elif "Status: Incorrect" in line:
                    incorrect_count += 1

        # Calculate and display accuracy
        total = correct_count + incorrect_count
        if total > 0:
            accuracy = (correct_count / total) * 100
            st.write(f"Total Questions: {total}")
            st.write(f"Correct Answers: {correct_count}")
            st.write(f"Incorrect Answers: {incorrect_count}")
            st.write(f"**Overall Accuracy: {accuracy:.2f}%**")

            # Data for visualization
            data = {
                'Status': ['Correct', 'Incorrect'],
                'Count': [correct_count, incorrect_count]
            }
            df = pd.DataFrame(data)

            # Display as a table
            st.table(df)

            # Plotting a pie chart for visualizing accuracy
            fig, ax = plt.subplots()
            ax.pie(df['Count'], labels=df['Status'], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.write("No questions recorded yet.")

st.markdown("---")
