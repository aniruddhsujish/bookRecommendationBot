import asyncio
from embeddings.embedder import load_model, load_books, embed_books
from vectordb.client import get_client, create_collection, upsert_books

def main():
    # load books from disk
    books = load_books()
    print(f"Loaded {len(books)} books")

    # load embedding model
    model = load_model()

    # generate embeddings
    book_with_embeddings = embed_books(books, model)

    # set upm qdrant
    client = get_client()
    create_collection(client)

    # store in qdrant
    upsert_books(client, book_with_embeddings)
    print(f"Stored {len(book_with_embeddings)} books in Qdrant")

main()