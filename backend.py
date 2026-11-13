# backend.py
import os
import re
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from transformers import pipeline

# =========================
# CONFIG
# =========================
INDEX_NAME = "medicalbot"

# =========================
# CACHE VECTORSTORE ⚡
# =========================
@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Pinecone.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings
    )

vectorstore = load_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # 🔥 less noise

# =========================
# CACHE MODEL ⚡
# =========================
@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-large",   # ⚡ faster than large
        max_new_tokens=400,
        do_sample=False
    )

qa_pipeline = load_model()

# =========================
# HELPERS
# =========================
def clean_text(text):
    text = re.sub(r"/C\d+", "", text)  # remove weird codes
    text = re.sub(r"\s+", " ", text)
    text = text.replace("-", " ")      # fix broken words
    return text.strip()


def format_bullets(text):
    sentences = re.split(r"[.;]\s+", text)
    return "\n".join([f"- {s.strip()}" for s in sentences if len(s.strip()) > 15])


def extract_section(text, section):
    pattern = rf"{section}\s*[:\-]?\s*(.*?)(?=\n[A-Z][a-z ]+[:\-]|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

# =========================
# CONTEXT
# =========================
def get_context(query):
    docs = retriever.invoke(query)
    return "\n\n".join(clean_text(doc.page_content) for doc in docs)

# =========================
# ANSWER FUNCTION
# =========================
def generate_answer(query):
    context = get_context(query)

    if not context.strip():
        return "⚠️ No relevant medical information found."

    prompt = f"""
You are a medical assistant.

Extract information STRICTLY from the context and return ONLY in JSON format:

{{
"definition": "...",
"causes": ["...", "..."],
"symptoms": ["...", "..."],
"treatment": ["...", "..."],
"doctor": ["...", "..."]
}}

Rules:
- Do not add extra text
- Do not explain outside JSON
- Keep answers short and clear

Context:
{context}

Question:
{query}
"""

    raw = qa_pipeline(prompt)[0]["generated_text"]

    # -------------------------
    # SAFE PARSING
    # -------------------------
    import json

    try:
        data = json.loads(raw)
    except:
        return "⚠️ Could not generate structured answer. Try again."

    # -------------------------
    # FORMAT OUTPUT
    # -------------------------
    def format_list(items):
        if not items:
            return "- Not clearly mentioned"
        return "\n".join([f"- {i}" for i in items])

    final = "## 🧠 Medical Answer\n\n"

    final += f"### Definition\n- {data.get('definition','Not found')}\n\n"
    final += f"### Causes\n{format_list(data.get('causes',[]))}\n\n"
    final += f"### Symptoms\n{format_list(data.get('symptoms',[]))}\n\n"
    final += f"### Treatment\n{format_list(data.get('treatment',[]))}\n\n"
    final += f"### When to see a doctor\n{format_list(data.get('doctor',[]))}\n\n"

    return final