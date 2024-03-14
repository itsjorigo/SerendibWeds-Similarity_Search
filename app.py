from flask import jsonify, request
from config import app, collection_name, model, dbClient

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


@app.route('/get_top_matches', methods=['POST'])
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

if __name__ == "__main__":
    app.run(debug=True)
