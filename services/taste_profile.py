import numpy as np
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from db.ratings import get_ratings
from vectordb.client import COLLECTION_NAME
from services.recommender import get_book_by_title, find_similar_books

def compute_taste_vector(client: QdrantClient) -> list[float] | None:
    ratings = get_ratings()

    if not ratings:
        return None
    
    liked = [r for r in ratings if r['rating'] == 1]
    disliked = [r for r in ratings if r['rating'] == -1]

    liked_vectors = []
    disliked_vectors = []

    for rating in liked:
        book = get_book_by_title(rating["title"], client)
        if book:
            liked_vectors.append(book["vector"])

    for rating in disliked:
        book = get_book_by_title(rating["title"], client)
        if book:
            disliked_vectors.append(book["vector"])

    if not liked_vectors:
        return None
    
    taste_vector = np.mean(liked_vectors, axis=0)

    if disliked_vectors:
        dislike_vector = np.mean(disliked_vectors, axis=0)
        taste_vector = taste_vector - (0.5 * dislike_vector)

    return taste_vector.tolist()

def discover_books(client: QdrantClient, limit: int = 5) -> list[dict]:
    taste_vector = compute_taste_vector(client)

    if taste_vector is None:
        return []
    
    return find_similar_books(
        query_vector=taste_vector,
        client=client,
        limit=limit
    )