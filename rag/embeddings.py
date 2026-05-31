import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",  # YES — go back to OLD format BUT correct API path
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )