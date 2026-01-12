import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"
INDEX_FILE = "faiss_S2_M2_bge-m3_IP.bin"
CHUNK_FILE = "chunks_S2.txt"

model = SentenceTransformer(MODEL_NAME)
index = faiss.read_index(INDEX_FILE)

with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = [line.strip() for line in f.readlines()]

def retrieve(query, top_k=3):
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)
    return [chunks[i] for i in indices[0]]
