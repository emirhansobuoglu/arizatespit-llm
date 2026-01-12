import faiss
import json
import time
import psutil
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# ================= CONFIG =================

FAISS_INDEX_PATH = "faiss_S2_M2_bge-m3_IP.bin"
CHUNKS_PATH = "chunks_S2.txt"
EMBED_MODEL = "BAAI/bge-m3"

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "phi3:mini",
    "gemma:2b",
    "qwen2.5:3b",
    "llama3.2:3b"
]

QUESTION = "Buzdolabımın içi karlanıyor, nedeni ne olabilir?"
TOP_K = 5
OUTPUT_FILE = "llm_comparison_results.json"

# ================= LOAD =================

embedder = SentenceTransformer(EMBED_MODEL)
index = faiss.read_index(FAISS_INDEX_PATH)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = [c.strip() for c in f.readlines()]

# ================= RETRIEVER =================

def retrieve(query, k):
    q_emb = embedder.encode([query], normalize_embeddings=True)
    scores, ids = index.search(np.array(q_emb), k)
    return [chunks[i] for i in ids[0]]

# ================= OLLAMA CALL =================

def ask_ollama(model, question, context):
    prompt = f"""
You are an assistant that answers questions using the provided context.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Use only the information in the context.
- If the answer is not in the context, say "I don't know based on the given documents."
- Answer concisely in Turkish.
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    cpu_before = psutil.cpu_percent(interval=None)
    ram_before = psutil.virtual_memory().used / 1024 / 1024

    start = time.time()
    r = requests.post(OLLAMA_URL, json=payload)
    end = time.time()

    cpu_after = psutil.cpu_percent(interval=None)
    ram_after = psutil.virtual_memory().used / 1024 / 1024

    data = r.json()

    answer = data.get("response", "").strip()
    tokens = data.get("eval_count", 0)
    latency = end - start

    return {
        "answer": answer,
        "latency_sec": round(latency, 3),
        "tokens": tokens,
        "tokens_per_sec": round(tokens / latency, 2) if latency > 0 else 0,
        "cpu_usage_percent": round(cpu_after - cpu_before, 2),
        "ram_usage_mb": round(ram_after - ram_before, 2),
        "model": model
    }

# ================= RUN =================

retrieved_chunks = retrieve(QUESTION, TOP_K)
context_text = "\n\n".join(retrieved_chunks)

results = []

for model in MODELS:
    print(f"▶ Running {model}")
    result = ask_ollama(model, QUESTION, context_text)
    result["question"] = QUESTION
    result["top_k"] = TOP_K
    results.append(result)

# ================= SAVE =================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ DONE")
print(f"📁 Results saved to: {OUTPUT_FILE}")
