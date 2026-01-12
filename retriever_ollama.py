import faiss
import numpy as np
import time
import requests
from sentence_transformers import SentenceTransformer

# =======================
# CONFIG
# =======================
FAISS_INDEX_PATH = "faiss_S2_M2_bge-m3_IP.bin"
CHUNKS_PATH = "chunks_S2.txt"

EMBED_MODEL = "BAAI/bge-m3"
OLLAMA_MODEL = "llama3.2:3b"
TOP_K = 5

OUTPUT_FILE = "ollama_results.jsonl"
OLLAMA_URL = "http://localhost:11434/api/generate"


# =======================
# LOAD CHUNKS
# =======================
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = [line.strip() for line in f.readlines()]

print(f"Toplam {len(chunks)} chunk yüklendi.")


# =======================
# LOAD FAISS
# =======================
index = faiss.read_index(FAISS_INDEX_PATH)

print("Embedding modeli yükleniyor...")
embed_model = SentenceTransformer(EMBED_MODEL)


# =======================
# RETRIEVE
# =======================
def retrieve(query, k=TOP_K):
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    scores, idx = index.search(q_emb, k)
    return [chunks[i] for i in idx[0]]


# =======================
# ASK OLLAMA
# =======================
def ask_ollama(question, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""<s>[INST]
You are an assistant that answers questions using the provided context.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Use only the information in the context.
- If the answer is not in the context, say "I don't know based on the given documents."
- Answer concisely in Turkish.
[/INST]
"""

    start_time = time.time()

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 256
            }
        }
    )

    elapsed = time.time() - start_time
    data = r.json()

    response = data.get("response", "")
    tokens = len(response.split())

    return {
        "answer": response,
        "latency_sec": round(elapsed, 3),
        "tokens": tokens,
        "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0
    }


# =======================
# RUN TEST
# =======================
def run_question(question):
    retrieved = retrieve(question)

    result = ask_ollama(question, retrieved)

    record = {
        "question": question,
        "top_k": TOP_K,
        "retrieved_chunks": retrieved,
        "answer": result["answer"],
        "latency_sec": result["latency_sec"],
        "tokens": result["tokens"],
        "tokens_per_sec": result["tokens_per_sec"],
        "model": OLLAMA_MODEL
    }

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(str(record) + "\n")

    return record


# =======================
# EXAMPLE
# =======================
if __name__ == "__main__":
    q = "Buzdolabımın içi karlanıyor, nedeni ne olabilir?"
    out = run_question(q)

    print("\n=== CEVAP ===")
    print(out["answer"])
    print("\nLatency:", out["latency_sec"], "sn")
    print("Token/s:", out["tokens_per_sec"])
