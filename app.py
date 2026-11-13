import streamlit as st

from backend import generate_answer


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MediBot - Medical Information Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. STYLING (colorful, forced light theme)
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Public+Sans:wght@400;500;600&display=swap');

    :root {
        color-scheme: light;
        --ink: #1E2A4A;
        --muted: #5B6785;
        --teal: #0EA5A4;
        --blue: #2563EB;
        --indigo: #6D4AE0;
        --pink: #EC4899;
        --orange: #F97316;
        --line: #DCE4F5;
    }

    html, body, .stApp, [data-testid="stSidebar"] {
        font-family: 'Public Sans', sans-serif;
        color-scheme: light;
    }

    /* ---------- Page background ---------- */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background:
            radial-gradient(circle at 0% 0%, #E0F7F6 0%, transparent 40%),
            radial-gradient(circle at 100% 0%, #EAE6FF 0%, transparent 40%),
            radial-gradient(circle at 100% 100%, #FFE9F3 0%, transparent 40%),
            #F7FAFF !important;
        color: var(--ink);
    }

    /* ---------- REMOVE BLACK AREAS ---------- */

    /* top header bar */
    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: transparent !important;
        color: var(--ink) !important;
    }
    [data-testid="stToolbar"] *,
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] svg {
        color: var(--ink) !important;
    }
    .stDeployButton,
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* bottom strip that holds the chat input */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 820px;
        padding-top: 3.5rem;
        padding-bottom: 6rem;
    }

    #MainMenu, footer { visibility: hidden; }

    /* ---------- Hero banner ---------- */
    .mb-hero {
        background: linear-gradient(120deg, #0EA5A4 0%, #2563EB 55%, #6D4AE0 100%);
        border-radius: 20px;
        padding: 26px 28px;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.25);
        margin-bottom: 16px;
    }
    .mb-hero-logo {
        width: 62px; height: 62px;
        border-radius: 16px;
        background: rgba(255,255,255,0.20);
        border: 1px solid rgba(255,255,255,0.35);
        display: flex; align-items: center; justify-content: center;
        font-size: 34px;
        flex-shrink: 0;
    }
    .mb-hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 30px; font-weight: 700; line-height: 1.15;
        color: #fff;
    }
    .mb-hero-sub {
        font-size: 16px; opacity: 0.95; margin-top: 4px; color: #fff;
    }

    /* ---------- Emergency notice ---------- */
    .mb-alert {
        background: linear-gradient(90deg, #FFF1E6, #FFE9EC);
        border: 1px solid #FBC9B0;
        border-left: 6px solid var(--orange);
        color: #7A2E0E;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* ---------- Welcome ---------- */
    .mb-welcome h2 {
        font-family: 'Poppins', sans-serif;
        font-size: 24px; font-weight: 600; color: var(--ink);
        margin: 6px 0 6px 0;
    }
    .mb-welcome p {
        font-size: 16px; color: var(--muted); line-height: 1.7; margin: 0 0 16px 0;
    }

    /* ---------- Buttons (base) ---------- */
    .stButton button {
        background: #FFFFFF;
        color: var(--ink);
        border: 1px solid var(--line);
        border-radius: 14px;
        min-height: 56px;
        font-size: 15.5px;
        font-weight: 600;
        text-align: left;
        justify-content: flex-start;
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton button p { color: inherit !important; }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(30, 42, 74, 0.12);
    }
    .stButton button:focus-visible {
        outline: 3px solid rgba(37, 99, 235, .35);
    }

    /* ---------- Colorful suggestion cards ---------- */
    .st-key-sq_0 button {
        background: linear-gradient(135deg, #E3F8F7, #FFFFFF);
        border: 1px solid #9ADCD9; border-left: 6px solid var(--teal);
    }
    .st-key-sq_1 button {
        background: linear-gradient(135deg, #E6EEFF, #FFFFFF);
        border: 1px solid #A9C1F5; border-left: 6px solid var(--blue);
    }
    .st-key-sq_2 button {
        background: linear-gradient(135deg, #FFEAF4, #FFFFFF);
        border: 1px solid #F5B4D4; border-left: 6px solid var(--pink);
    }
    .st-key-sq_3 button {
        background: linear-gradient(135deg, #FFF0E3, #FFFFFF);
        border: 1px solid #F8C79F; border-left: 6px solid var(--orange);
    }

    /* ---------- Chat messages ---------- */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 14px;
        background: #FFFFFF !important;
        border: 1px solid var(--line);
        border-left: 6px solid var(--teal);
        box-shadow: 0 4px 14px rgba(30, 42, 74, 0.06);
    }
    /* user messages: purple tint */
    [class*="st-key-user_msg"] [data-testid="stChatMessage"],
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #EEE9FF, #F6F3FF) !important;
        border: 1px solid #D5CBFA;
        border-left: 6px solid var(--indigo);
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        font-size: 16.5px;
        line-height: 1.75;
        color: var(--ink) !important;
    }

    /* avatars: soft colors instead of black circles */
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="chatAvatarIcon-assistant"] {
        background: #D7F3F2 !important;
        color: var(--ink) !important;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="chatAvatarIcon-user"] {
        background: #E3DBFF !important;
        color: var(--ink) !important;
    }

    /* ---------- Chat input (white box, dark text) ---------- */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] div[data-baseweb="textarea"],
    [data-testid="stChatInput"] div[data-baseweb="base-input"] {
        background: #FFFFFF !important;
    }
    [data-testid="stChatInput"] {
        border: 2px solid #B9C9F5 !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.10);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--indigo) !important;
        box-shadow: 0 0 0 4px rgba(109, 74, 224, 0.15);
    }
    [data-testid="stChatInput"] textarea {
        background: #FFFFFF !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        font-size: 16.5px;
        caret-color: var(--indigo);
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #7B86A3 !important;
        -webkit-text-fill-color: #7B86A3 !important;
        opacity: 1;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #0EA5A4, #6D4AE0) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    /* ---------- Sources / expanders (white, not black) ---------- */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #CFE0F7 !important;
        border-left: 5px solid var(--blue) !important;
        border-radius: 12px;
        margin-top: 10px;
    }
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #FFFFFF !important;
        color: var(--ink) !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        color: var(--ink) !important;
        font-weight: 600;
    }
    [data-testid="stExpander"] [data-testid="stCaptionContainer"],
    [data-testid="stExpander"] [data-testid="stCaptionContainer"] * {
        color: #4D5A78 !important;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #DDF6F5 0%, #E8E9FF 55%, #FFE7F2 100%) !important;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li { font-size: 15px; line-height: 1.7; color: var(--ink) !important; }
    [data-testid="stSidebar"] h3 { font-family: 'Poppins', sans-serif; color: var(--ink); }

    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #0EA5A4, #2563EB);
        color: #FFFFFF !important;
        border: none;
        justify-content: center;
        text-align: center;
    }
    [data-testid="stSidebar"] .stButton button p { color: #FFFFFF !important; }

    .mb-disclaimer {
        font-size: 13px;
        color: var(--muted);
        line-height: 1.6;
        text-align: center;
        padding-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. CONSTANTS & SESSION STATE
# ============================================================

SUGGESTED_QUESTIONS = [
    "🤧 Explain the common cold.",
    "❤️ What causes high blood pressure?",
    "🩸 What is diabetes?",
    "🧬 What are the symptoms of anemia?",
]

# Text sent to the backend (without the emoji)
QUESTION_TEXT = [
    "Explain the common cold.",
    "What causes high blood pressure?",
    "What is diabetes?",
    "What are the symptoms of anemia?",
]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# ============================================================
# 4. HELPERS
# ============================================================

def prepare_sources(docs):
    """Turn retrieved documents into a de-duplicated list of dicts."""
    sources, seen = [], set()

    for doc in docs or []:
        metadata = getattr(doc, "metadata", {}) or {}
        content = getattr(doc, "page_content", "") or ""

        source = metadata.get("source", "Medical Encyclopedia")
        page = metadata.get("page_label", metadata.get("page", "Not available"))
        filename = str(source).replace("\\", "/").split("/")[-1]

        key = (filename, str(page), content[:200])
        if key in seen:
            continue
        seen.add(key)

        sources.append({"filename": filename, "page": str(page), "content": content})

    return sources


def display_sources(sources):
    if not sources:
        return

    with st.expander(f"📚 Sources used for this answer ({len(sources)})"):
        for i, src in enumerate(sources, start=1):
            st.markdown(f"**{i}. {src['filename']}**  ·  page {src['page']}")
            text = src["content"]
            st.caption(text[:700] + ("…" if len(text) > 700 else ""))
            if i < len(sources):
                st.divider()


def render_message(role, content, sources=None, idx=0):
    """Draw one chat message inside a keyed container (used for styling)."""
    avatar = "🧑" if role == "user" else "🩺"
    with st.container(key=f"{role}_msg_{idx}"):
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if role == "assistant":
                display_sources(sources or [])


def set_pending(question):
    st.session_state.pending_query = question


def reset_chat():
    st.session_state.messages = []
    st.session_state.pending_query = None


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🩺 MediBot")
    st.caption("Medical information from a trusted encyclopedia")

    st.button("＋ New chat", use_container_width=True, on_click=reset_chat)

    st.divider()

    st.markdown("**How it works**")
    st.write(
        "MediBot looks up relevant passages in a medical encyclopedia, "
        "then uses an AI model to write an answer based on them. "
        "Open **Sources** under any answer to see where it came from."
    )

    st.divider()

    st.markdown("**Good to know**")
    st.write(
        "- Answers are for learning, not diagnosis.\n"
        "- AI can make mistakes. Check important details with a doctor.\n"
        "- Don't enter personal or identifying information."
    )

    with st.expander("Technology"):
        st.write(
            "Python · Streamlit · LangChain · Pinecone · "
            "Hugging Face · Sentence Transformers · FLAN-T5 Large"
        )


# ============================================================
# 6. HERO BANNER + EMERGENCY NOTICE
# ============================================================

st.markdown(
    """
    <div class="mb-hero">
        <div class="mb-hero-logo">🩺</div>
        <div>
            <div class="mb-hero-title">MediBot</div>
            <div class="mb-hero-sub">Your friendly guide to diseases, symptoms, causes and treatments</div>
        </div>
    </div>
    <div class="mb-alert">
        <b>Not for emergencies.</b> If you or someone else has severe symptoms
        such as chest pain, trouble breathing or heavy bleeding, call your
        local emergency number right away.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 7. WELCOME (only on an empty chat)
# ============================================================

if not st.session_state.messages and not st.session_state.pending_query:
    st.markdown(
        """
        <div class="mb-welcome">
            <h2>What would you like to know?</h2>
            <p>Type a question below, or tap one of these to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, label in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            st.button(label, key=f"sq_{i}", use_container_width=True,
                      on_click=set_pending, args=(QUESTION_TEXT[i],))


# ============================================================
# 8. CHAT HISTORY
# ============================================================

for i, message in enumerate(st.session_state.messages):
    render_message(
        message["role"],
        message["content"],
        message.get("sources", []),
        idx=i,
    )


# ============================================================
# 9. INPUT
# ============================================================

typed_query = st.chat_input("Ask a medical question…")
user_query = st.session_state.pending_query or typed_query


# ============================================================
# 10. GENERATE ANSWER
# ============================================================

if user_query:
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": user_query})

    next_idx = len(st.session_state.messages)
    render_message("user", user_query, idx=next_idx - 1)

    with st.container(key=f"assistant_msg_{next_idx}"):
        with st.chat_message("assistant", avatar="🩺"):
            try:
                with st.spinner("Searching the encyclopedia and writing an answer…"):
                    result = generate_answer(user_query)

                if isinstance(result, tuple):
                    answer = result[0]
                    docs = result[1] if len(result) > 1 else []
                else:
                    answer, docs = result, []

                if not answer:
                    answer = ("I couldn't find an answer to that. "
                              "Try rephrasing your question or using a more specific term.")

                sources = prepare_sources(docs)
                reply = {"role": "assistant", "content": str(answer), "sources": sources}

            except Exception as error:
                st.session_state.last_error = str(error)
                reply = {
                    "role": "assistant",
                    "content": ("Something went wrong while generating the answer. "
                                "Please try again in a moment."),
                    "sources": [],
                }

    st.session_state.messages.append(reply)
    st.rerun()


# ============================================================
# 11. DISCLAIMER
# ============================================================

st.markdown(
    '<div class="mb-disclaimer">⚕️ MediBot gives educational information only. '
    'It does not replace professional medical advice, diagnosis or treatment. '
    'Always consult a qualified healthcare professional.</div>',
    unsafe_allow_html=True,
)