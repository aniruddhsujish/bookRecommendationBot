from vectordb.client import get_client, create_collection
from embeddings.embedder import load_model
from db.ratings import init_db

client = get_client()
create_collection(client)
model = load_model()
init_db()
