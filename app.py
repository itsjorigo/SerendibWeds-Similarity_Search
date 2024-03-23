import csv
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def initialize_qdrant_client():
    try:
        # qdrant_url = os.getenv("QDRANT_URL")  # Fetch URL from environment variable
        qdrant_url = "https://e3541770-0ff4-4afd-82a7-1fcd383f93c9.us-east4-0.gcp.cloud.qdrant.io:6333"

        # qdrant_api_key = os.getenv("QDRANT_API_KEY")  # Fetch API key from environment variable
        qdrant_api_key = "2qW8PUMwWLxGl4B7h-vK3CKrafvIiaYsk40wuVFFOzFp3yukdEbZ6Q"
        return QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    except Exception as e:
        logger.error(f"Error initializing Qdrant client: {e}")
        return None
    

def initialize_sentence_transformer_model():
    try:
        return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    except Exception as e:
        logger.error(f"Error initializing SentenceTransformer model: {e}")
        return None

def read_data(file_path):
    try:
        data = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        logger.error(f"Error reading data from file: {e}")
        return []

def validate_search_query(search_query):
    if not search_query or not isinstance(search_query, str):
        return False
    return  True


def process_search_query(search_query, dbClient, collection_name, model):
    search_query_embedding = model.encode([search_query])[0]
    hits = dbClient.search(
        collection_name=collection_name,
        query_vector=search_query_embedding,
        limit=6
    )
    similar_matches = []
    for hit in hits:
        similar_matches.append({
            "id": hit.id,
            "vector": hit.vector,
            "metadata": hit.payload
        })
    return similar_matches


@app.route('/get_top_matches', methods = ['POST'])
def get_top_matches():
    try:
        dbClient = initialize_qdrant_client()
        collection_name = "SerendibWeds_weddings_dataset"

        # Initialize SentenceTransformer model
        model = initialize_sentence_transformer_model()

        search_query = request.json.get('searchQuery')
        
        if not validate_search_query(search_query):
            return jsonify({"error": "Invalid search query format"}), 400
        
        similar_matches = process_search_query(search_query, dbClient, collection_name, model)
        return jsonify(similar_matches), 200
    
    except Exception as e:
        error_message = {"error": str(e)}
        logger.error(f"Error processing request: {error_message}")
        return jsonify(error_message), 500
    

if __name__ == "__main__":
    app.run(debug=False)
