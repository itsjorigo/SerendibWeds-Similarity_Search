import csv
from flask import jsonify, request
from config import dbClient, collection_name
from sentence_transformers import SentenceTransformer
from qdrant_client.http.models import PointStruct, VectorParams, Distance

def read_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def upsert_to_qdrant():
        file_path = 'SerendibWedstest.csv'
        try:
            data = read_data(file_path)
            if data:
                descriptions = [row['description'] for row in data]

                model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                embeddings = model.encode(descriptions)

                client = dbClient
                column_names = data[0].keys()
                vector_size = len(embeddings[0])

                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )

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
                print("Data indexed successfully.")
            else:
                print("No data found in the CSV file.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    upsert_to_qdrant()
    