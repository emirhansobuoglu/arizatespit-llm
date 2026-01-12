import json
import re
from collections import Counter

# --------------------------------------------------
# BASIC TEXT UTILS
# --------------------------------------------------

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def exact_match(pred, gold):
    return int(normalize(pred) == normalize(gold))

def f1_score(pred, gold):
    pred_tokens = normalize(pred).split()
    gold_tokens = normalize(gold).split()

    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)

    return 2 * precision * recall / (precision + recall)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with open("llm_only_outputs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = []

# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

for item in data:
    em = exact_match(item["answer"], item["expected_answer"])
    f1 = f1_score(item["answer"], item["expected_answer"])

    # very simple hallucination heuristic
    hallucinated = int(len(item["answer"].strip()) > 300 and f1 < 0.2)

    results.append({
        "model": item["model"],
        "EM": em,
        "F1": round(f1, 4),
        "hallucinated": hallucinated
    })

# --------------------------------------------------
# REPORT
# --------------------------------------------------

print("\n========= LLM-ONLY PERFORMANCE =========\n")

for r in results:
    print(f"Model: {r['model']}")
    print(f"  Exact Match: {r['EM']}")
    print(f"  F1-score: {r['F1']}")
    print(f"  Hallucination: {r['hallucinated']}")
    print("-" * 40)

hall_rate = sum(r["hallucinated"] for r in results) / len(results)
print(f"\nHallucination Rate: {hall_rate:.2f}")
