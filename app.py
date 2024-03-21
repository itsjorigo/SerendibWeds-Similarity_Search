import os
import csv
from flask import jsonify, request
from sentence_transformers import SentenceTransformer
from config import app, collection_name, model, dbClient
from qdrant_client.models import Filter, FieldCondition, Range
from qdrant_client.http.models import PointStruct, VectorParams, Distance

def read_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def validate_search_query(search_query):
    if not search_query or not isinstance(search_query, str):
        return False
    return  True


def process_search_query(search_query):
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
        search_query = request.json.get('searchQuery')
        
        if not validate_search_query(search_query):
            return jsonify({"error": "Invalid search query format"}), 400
        
        similar_matches = process_search_query(search_query)
        return jsonify(similar_matches), 200
    
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500
    

@app.route('/submit-wedding-data', methods=['POST'])
def upsert_to_qdrant():
        file_path = 'weddingData.csv'
        try:
            data = request.json.get('weddingQuery')
            if data:
                descriptions = [row['description'] for row in data]

                model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                embeddings = model.encode(descriptions)

                client = dbClient
                column_names = data[0].keys()
                vector_size = len(embeddings[0])

                for i, (embedding, row) in enumerate(zip(embeddings, data)):
                    wedding_data = {column: row[column] for column in column_names}

                    progress_info = client.upsert(
                        collection_name=collection_name,
                        points=[
                            PointStruct(
                                id=i,
                                vector=embedding.tolist(),
                                payload=wedding_data
                            )
                        ]
                    )
                    print(progress_info)
                return jsonify({"message": "Data indexed successfully."}), 200
            else:
                return jsonify({"error": "No data found in the request."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
