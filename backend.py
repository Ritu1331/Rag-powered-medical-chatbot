
# ============================================================
# MEDICAL RAG CHATBOT - BACKEND
# LangChain | Pinecone | Hugging Face | FLAN-T5
# ============================================================

import os
import re
import streamlit as st

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from transformers import pipeline


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

INDEX_NAME = "medicalbot"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

LLM_MODEL = "google/flan-t5-large"

TOP_K = 5

MAX_INPUT_TOKENS = 512

MAX_NEW_TOKENS = 300


# ============================================================
# 2. PINECONE API KEY
# ============================================================

def get_pinecone_api_key():

    # Streamlit Cloud Secrets
    try:
        key = st.secrets.get("PINECONE_API_KEY")

        if key:
            return key.strip()

    except Exception:
        pass

    # Local .env file
    key = os.getenv("PINECONE_API_KEY")

    if key:
        return key.strip()

    raise ValueError(
        "PINECONE_API_KEY not found. "
        "Add it to your .env file or Streamlit Cloud Secrets."
    )


# ============================================================
# 3. LOAD EMBEDDINGS
# ============================================================

@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )


# ============================================================
# 4. CONNECT TO PINECONE
# ============================================================

@st.cache_resource
def load_vectorstore():

    os.environ["PINECONE_API_KEY"] = get_pinecone_api_key()

    embeddings = load_embeddings()

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings
    )

    return vectorstore


# ============================================================
# 5. CREATE RETRIEVER
# ============================================================

@st.cache_resource
def load_retriever():

    vectorstore = load_vectorstore()

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": TOP_K
        }
    )


# ============================================================
# 6. LOAD FLAN-T5 MODEL
# ============================================================

@st.cache_resource
def load_model():

    model = pipeline(
        task="text2text-generation",
        model=LLM_MODEL,
        device=-1
    )

    return model


# ============================================================
# 7. CLEAN PDF TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    # Remove PDF formatting codes
    text = re.sub(r"/C\d+", "", text)

    # Join words split across PDF line breaks
    # Example: medi-
    #          cal -> medical
    text = re.sub(r"-\s*\n\s*", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# 8. RETRIEVE DOCUMENTS
# ============================================================

def retrieve_documents(query):

    retriever = load_retriever()

    docs = retriever.invoke(query)

    unique_docs = []

    seen = set()

    for doc in docs:

        metadata = doc.metadata or {}

        content = clean_text(doc.page_content)

        source = metadata.get(
            "source",
            ""
        )

        page = metadata.get(
            "page_label",
            metadata.get("page", "")
        )

        unique_key = (
            str(source),
            str(page),
            content
        )

        if content and unique_key not in seen:

            seen.add(unique_key)

            unique_docs.append(doc)

    return unique_docs


# ============================================================
# 9. PREPARE MEDICAL CONTEXT
# ============================================================

def get_context(query):

    docs = retrieve_documents(query)

    context_parts = []

    for i, doc in enumerate(docs, start=1):

        content = clean_text(doc.page_content)

        if content:

            context_parts.append(
                f"Medical Source {i}:\n{content}"
            )

    context = "\n\n".join(context_parts)

    return context, docs


# ============================================================
# 10. BUILD MEDICAL PROMPT
# ============================================================

def build_prompt(query, context, tokenizer):

    """
    Build a prompt that prioritizes:
    1. Instructions
    2. User question
    3. Retrieved medical context

    Context is placed at the end so that when the
    512-token input limit is reached, the question
    and instructions are preserved.
    """

    prompt = f"""
You are MediBot, a helpful and responsible medical
knowledge assistant.

Your job is to explain medical information in simple,
clear and beginner-friendly English.

USER QUESTION:
{query}

IMPORTANT INSTRUCTIONS:

1. Answer the user's question directly.
2. Use only information supported by the reference material.
3. Explain medical terminology in simple language.
4. Do not copy large paragraphs directly from the source.
5. Organize the response using short headings and bullet points.
6. Include causes, symptoms, risk factors, prevention or
   treatment information only when relevant and supported
   by the reference material.
7. Explain important points rather than merely listing them.
8. Avoid unnecessary repetition.
9. Do not invent medical facts, statistics, medicines,
   dosages or treatments.
10. If the reference material does not answer the question,
    clearly explain that the available information is insufficient.
11. Write complete sentences and finish the explanation properly.
12. Do not diagnose the user or prescribe medication.
13. Keep the answer relevant to the exact question.

RESPONSE STYLE:

Start with a short direct answer.

Then use suitable sections such as:

Overview
Causes
Symptoms
Risk Factors
Prevention
Treatment Information

Use only the sections relevant to the question.
Do not create empty headings.

Finish with a short, relevant medical safety note
when appropriate.

REFERENCE MEDICAL MATERIAL:
{context}

Now write a clear, complete and informative answer
to the user's question.
"""

    # Tokenize the complete prompt.
    # Truncation removes content from the end, so the
    # user's question and instructions remain at the start.

    encoded_input = tokenizer(
        prompt,
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
        return_tensors="pt"
    )

    # Convert token IDs back to text for the pipeline.
    safe_prompt = tokenizer.decode(
        encoded_input["input_ids"][0],
        skip_special_tokens=True
    )

    return safe_prompt


# ============================================================
# 11. GENERATE MEDICAL ANSWER
# ============================================================

def generate_answer(query):

    if not query or not query.strip():

        return (
            "Please enter a medical question.",
            []
        )

    query = query.strip()

    try:

        # --------------------------------------------
        # STEP 1: RETRIEVE RELEVANT DOCUMENTS
        # --------------------------------------------

        context, docs = get_context(query)

        if not context.strip():

            return (
                "No relevant information was found in the "
                "medical encyclopedia. Please try rephrasing "
                "your question or consult a qualified "
                "healthcare professional.",
                docs
            )

        # --------------------------------------------
        # STEP 2: LOAD MODEL
        # --------------------------------------------

        qa_model = load_model()

        tokenizer = qa_model.tokenizer

        # --------------------------------------------
        # STEP 3: BUILD PROMPT
        # --------------------------------------------

        prompt = build_prompt(
            query=query,
            context=context,
            tokenizer=tokenizer
        )

        # --------------------------------------------
        # STEP 4: GENERATE ANSWER
        # --------------------------------------------

        response = qa_model(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=4,
            do_sample=False,
            early_stopping=True,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3
        )

        answer = response[0]["generated_text"].strip()

        # --------------------------------------------
        # STEP 5: HANDLE EMPTY ANSWERS
        # --------------------------------------------

        if not answer:

            answer = (
                "I could not generate an answer from the "
                "available medical information. "
                "Please try rephrasing your question."
            )

        # --------------------------------------------
        # STEP 6: RETURN ANSWER AND SOURCES
        # --------------------------------------------

        return answer, docs

    except Exception as error:

        print("Medical RAG backend error:", str(error))

        raise


# ============================================================
# 12. BACKEND TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 55)
    print("MEDICAL RAG CHATBOT BACKEND TEST")
    print("=" * 55)

    question = input("\nEnter your medical question: ")

    try:

        answer, sources = generate_answer(question)

        print("\n" + "=" * 55)
        print("MEDICAL ANSWER")
        print("=" * 55)

        print(answer)

        print("\n" + "=" * 55)
        print("RETRIEVED MEDICAL SOURCES")
        print("=" * 55)

        for i, doc in enumerate(sources, start=1):

            metadata = doc.metadata or {}

            print(f"\nSource {i}")

            print(
                "File:",
                metadata.get("source", "Unknown")
            )

            print(
                "Page:",
                metadata.get(
                    "page_label",
                    metadata.get("page", "Unknown")
                )
            )

            print("-" * 45)

    except Exception as error:

        print("\nBackend error:", str(error))
