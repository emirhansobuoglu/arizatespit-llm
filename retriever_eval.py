import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# ===============================
# AYARLAR
# ===============================
MODEL_NAME = "BAAI/bge-m3"
INDEX_FILE = "faiss_S2_M2_bge-m3_IP.bin"
CHUNK_FILE = "chunks_S2.txt"
EVAL_FILE = "eval_questions.csv"

TOP_K_VALUES = [1, 3, 5]

# ===============================
# MODEL + INDEX YÜKLE
# ===============================
print("🔄 Model yükleniyor...")
model = SentenceTransformer(MODEL_NAME)

print("🔄 FAISS index yükleniyor...")
index = faiss.read_index(INDEX_FILE)

print("🔄 Chunk dosyası yükleniyor...")
with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = [line.strip() for line in f.readlines()]

print(f"Toplam {len(chunks)} chunk yüklendi.\n")

# ===============================
# RETRIEVE FONKSİYONU
# ===============================
def retrieve(query, top_k=3):
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)
    return [chunks[i] for i in indices[0]]

# ===============================
# TOP-K CHUNK GÖSTERME
# ===============================
def show_topk_chunks(query, top_k=3):
    print(f"\n🔍 SORU: {query}")
    results = retrieve(query, top_k)

    for i, chunk in enumerate(results, 1):
        print(f"\n--- TOP {i} ---")
        print(chunk[:600])  # çok uzunsa kesiyoruz

# ===============================
# EVALUATION (RECALL / HIT@K)
# ===============================
def evaluate_retriever():
    df = pd.read_csv(EVAL_FILE)

    results = {k: 0 for k in TOP_K_VALUES}
    total = len(df)

    for _, row in df.iterrows():
        question = row["soru"]
        gt = str(row["ground_truth"]).lower()

        retrieved = retrieve(question, max(TOP_K_VALUES))

        for k in TOP_K_VALUES:
            topk_chunks = retrieved[:k]
            hit = any(gt in chunk.lower() for chunk in topk_chunks)
            if hit:
                results[k] += 1

    print("\n📊 RETRIEVER EVALUATION SONUÇLARI")
    print("================================")
    for k in TOP_K_VALUES:
        recall = results[k] / total
        print(f"Recall@{k} / Hit@{k}: {recall:.4f}")

if __name__ == "__main__":
    # 1️⃣ Top-k chunk örneği göster
    show_topk_chunks(
        "Buzdolabımın içi karlanıyor, nedeni ne olabilir?",
        top_k=3
    )

    evaluate_retriever()
