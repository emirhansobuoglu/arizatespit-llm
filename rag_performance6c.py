import time
import json
import re
import psutil
import requests
from collections import Counter

# ===================== CONFIG =====================
OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "phi3:mini",
    "gemma:2b",
    "llama3.2:3b",
    "qwen2.5:3b"
]

QUESTION = "Buzdolabımın içi karlanıyor, nedeni ne olabilir?"
TOP_K = 5

EXPECTED_ANSWER = """
Buzdolabında karlanma genellikle fan arızası, defrost (rezistans/NTC) problemi,
kapının uzun süre açık kalması veya nemli hava girişi nedeniyle oluşur.
"""

# ===================== METRICS =====================
def normalize(text):
    return re.sub(r"\W+", " ", text.lower()).strip()

def exact_match(pred, ref):
    return int(normalize(pred) == normalize(ref))

def f1_score(pred, ref):
    pred_tokens = normalize(pred).split()
    ref_tokens = normalize(ref).split()

    common = Counter(pred_tokens) & Counter(ref_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(ref_tokens)
    return round((2 * precision * recall) / (precision + recall), 4)

def hallucination(pred, chunks):
    combined_chunks = normalize(" ".join(chunks))
    pred_words = set(normalize(pred).split())
    chunk_words = set(combined_chunks.split())

    extra_words = pred_words - chunk_words
    return int(len(extra_words) > len(pred_words) * 0.4)

# ===================== RETRIEVER (SABİT INPUT) =====================
# SENİN MEVCUT retriever çıktın
RETRIEVED_CHUNKS = [
    "Fan çalışmıyorsa veya sorunluysa hava sirkülasyonu olmaz ve karlanma oluşur.",
    "Defrost rezistansı veya NTC arızası buzlanmaya sebep olabilir.",
    "Kapı uzun süre açık kalırsa nemli hava girer ve karlanma yapar.",
    "Fazla gaz basılması evaporatörde karlanma oluşturabilir.",
    "Nemli havalarda çekmecelerde geçici karlanma olabilir."
]

def build_prompt(question, chunks):
    context = "\n".join(chunks)
    return f"""You are an assistant that answers questions using the provided context.
CONTEXT:
{context}
QUESTION:
{question}
INSTRUCTIONS:
- Use only the information in the context.
- If the answer is not in the context, say "I don't know based on the given documents."
- Answer concisely in Turkish.
"""


# ===================== LLM CALL =====================
def call_ollama(model, prompt):
    start = time.time()
    cpu_before = psutil.cpu_percent(interval=None)
    ram_before = psutil.virtual_memory().used / 1024 / 1024

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    ).json()

    latency = round(time.time() - start, 3)
    answer = response.get("response", "").strip()
    tokens = response.get("eval_count", 0)

    cpu_after = psutil.cpu_percent(interval=None)
    ram_after = psutil.virtual_memory().used / 1024 / 1024

    return {
        "answer": answer,
        "latency_sec": latency,
        "tokens": tokens,
        "tokens_per_sec": round(tokens / latency, 2) if latency > 0 else 0,
        "cpu_usage_percent": round(cpu_after - cpu_before, 2),
        "ram_usage_mb": round(ram_after - ram_before, 2)
    }

# ===================== MAIN =====================
results = []

for model in MODELS:
    prompt = build_prompt(QUESTION, RETRIEVED_CHUNKS)
    output = call_ollama(model, prompt)

    em = exact_match(output["answer"], EXPECTED_ANSWER)
    f1 = f1_score(output["answer"], EXPECTED_ANSWER)
    hall = hallucination(output["answer"], RETRIEVED_CHUNKS)

    results.append({
        "model": model,
        "question": QUESTION,
        "top_k": TOP_K,
        "answer": output["answer"],
        "Exact_Match": em,
        "F1_score": f1,
        "Hallucination": hall,
        "latency_sec": output["latency_sec"],
        "tokens": output["tokens"],
        "tokens_per_sec": output["tokens_per_sec"],
        "cpu_usage_percent": output["cpu_usage_percent"],
        "ram_usage_mb": output["ram_usage_mb"]
    })

# ===================== SAVE =====================
with open("rag_performance_6c.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ 6.C RAG Performance completed. Saved to rag_performance_6c.json")
