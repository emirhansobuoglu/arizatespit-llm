# Refrigerator Fault Diagnosis with RAG (Forum-Based LLM System)

This repository contains a **Retrieval-Augmented Generation (RAG)** based system developed for **refrigerator fault diagnosis** using real-world forum data.  
The goal of the project is to reduce hallucination in Large Language Models (LLMs) by grounding answers strictly on retrieved domain-specific documents.

The project was developed as part of an academic study focusing on **information retrieval, local LLM evaluation, and hallucination analysis**.

---

## 📌 Project Overview

Traditional LLMs tend to generate unreliable or hallucinated answers when asked domain-specific technical questions.  
To address this issue, this project implements a **RAG pipeline** that:

- Retrieves relevant solutions from real forum discussions
- Uses only retrieved context to generate answers
- Compares **Retriever-only**, **LLM-only**, and **RAG + LLM** systems

**Domain:** White goods / Refrigerator fault diagnosis  
**Language:** Turkish  
**Data Source:** Online technical support forums

---

## 🧱 System Architecture

User Question
↓
Embedding Model
↓
FAISS Vector Database
↓
Top-k Retrieved Chunks
↓
Local LLM (Ollama)
↓
Final Answer


---

## 📂 Repository Structure

.
├── chunking_faiss.py # Chunking, embedding and FAISS index creation
├── retriever.py # Retriever-only evaluation
├── retriever_ollama.py # RAG + LLM pipeline
├── llm_only_eval.py # LLM-only performance evaluation
├── evaluation.csv # Ground truth evaluation queries
├── requirements.txt
├── README.md
└── .gitignore


> ⚠️ Model weights, FAISS indexes, and generated outputs are intentionally excluded from the repository.

---

## 🧠 Chunking Strategies

Two different chunking strategies were evaluated:

1. **Sentence-based Chunking**
   - Preserves semantic integrity
   - Better suited for technical explanations

2. **Fixed-length Chunking with Overlap**
   - Ensures no information loss
   - Useful for long documents

---

## 🔢 Embedding Models

- **dbmdz/bert-base-turkish-cased**  
  Turkish-specific transformer model

- **BAAI/bge-m3**  
  High-performance multilingual embedding model

These embeddings were compared to analyze their impact on retrieval performance.

---

## 🗄️ Vector Database

- **FAISS (IndexFlatIP)**
- Exact similarity search
- Inner Product similarity (Cosine similarity via normalization)

Chosen for fast and accurate nearest-neighbor search on dense embeddings.

---

## 🧪 Evaluation Scenarios

### 1️⃣ Retriever-only
- Metrics: Recall@1, Recall@3, Recall@5
- Purpose: Measure retrieval quality independently

### 2️⃣ LLM-only (No RAG)
- No context provided
- Metrics:
  - Exact Match (EM)
  - F1-score
  - Hallucination Rate

### 3️⃣ RAG + LLM
- Retriever + Local LLM
- Metrics:
  - EM
  - F1-score
  - Hallucination Rate
  - Latency
  - Tokens / sec
  - CPU & RAM usage

---

## 🤖 Local LLMs Used (via Ollama)

- phi3:mini
- gemma:2b
- llama3.2:3b
- qwen2.5:3b

All models were evaluated **locally on CPU** due to hardware constraints.

---
Google Colab[https://colab.research.google.com/drive/1s4m9knY4UnsrtMPTutUesjPgvnlKUZlZ?usp=sharing]
