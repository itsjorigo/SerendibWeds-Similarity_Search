from flask import Flask
from flask_cors import CORS
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

def initialize_qdrant_client():
    try:
        return QdrantClient(
            url="https://e3541770-0ff4-4afd-82a7-1fcd383f93c9.us-east4-0.gcp.cloud.qdrant.io:6333",
            api_key="2qW8PUMwWLxGl4B7h-vK3CKrafvIiaYsk40wuVFFOzFp3yukdEbZ6Q",
        )
    except Exception as e:
        print(f"Error initializing Qdrant client: {e}")
        return None
    
        
def initialize_sentence_transformer_model():
    try:
        return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    except Exception as e:
        print(f"Error initializing SentenceTransformer model: {e}")
        return None
    

# Initialize Qdrant client and collection
dbClient = initialize_qdrant_client()
collection_name = "SerendibWeds_past_weddings"

# Initialize SentenceTransformer model
model = initialize_sentence_transformer_model()