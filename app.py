"""
frontend/app.py
================
Rural AI Assistant — Redesigned UI/UX
Fixes:
  1. Invisible answer text (white on white)
  2. TTS 404 error handling
  3. Full modern design with proper contrast
"""
import requests
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "🌾 Rural AI Assistant",
    page_icon  = "🌾",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ── Custom CSS — fixes ALL text visibility issues ─────────────────────────────
st.markdown("""
<style>
/* ── Global font & background ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* ── Answer card — dark text guaranteed ── */
.answer-card {
    background: #ffffff;
    border-left: 6px solid #2e7d32;
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
    color: #1a1a1a !important;
    font-size: 1rem;
    line-height: 1.9;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}

/* ── Intent badge ── */
.intent-badge {
    display: inline-block;
    background: #e8f5e9;
    color: #1b5e20;
    border: 1px solid #a5d6a7;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 10px;
}

/* ── Stat cards row ── */
.stat-row {
    display: flex;
    gap: 12px;
    margin: 14px 0;
}
.stat-card {
    flex: 1;
    background: #f9fbe7;
    border: 1px solid #c5e1a5;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
    color: #33691e;
    font-size: 0.82rem;
    font-weight: 600;
}

/* ── Weather box ── */
.weather-box {
    background: #e3f2fd;
    border-left: 5px solid #1976d2;
    border-radius: 8px;
    padding: 14px 18px;
    color: #0d47a1 !important;
    font-size: 0.92rem;
    line-height: 1.8;
    white-space: pre-line;
    margin: 10px 0;
}

/* ── Error box ── */
.error-box {
    background: #fff3e0;
    border-left: 5px solid #e65100;
    border-radius: 8px;
    padding: 14px 18px;
    color: #bf360c !important;
    font-size: 0.92rem;
    line-height: 1.8;
    white-space: pre-line;
    margin: 10px 0;
}

/* ── Source tag ── */
.source-tag {
    display: inline-block;
    background: #ede7f6;
    color: #4527a0;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: monospace;
    font-size: 0.82rem;
    margin: 2px 4px;
}

/* ── Section header ── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1b5e20;
    border-bottom: 2px solid #a5d6a7;
    padding-bottom: 6px;
    margin: 18px 0 10px 0;
}

/* ── Fix Streamlit's default text colors in dark mode ── */
.stMarkdown p, .stMarkdown li {
    color: inherit;
}

/* ── Sidebar status dots ── */
.status-ok   { color: #2e7d32; font-weight: bold; }
.status-err  { color: #c62828; font-weight: bold; }
.status-warn { color: #e65100; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

API_BASE   = "http://localhost:8000/api"
OLLAMA_URL = "http://localhost:11434"

LANGUAGES = {
    "🇬🇧 English":             ("english",   "en"),
    "🇮🇳 हिंदी (Hindi)":       ("hindi",     "hi"),
    "🇮🇳 தமிழ் (Tamil)":       ("tamil",     "ta"),
    "🇮🇳 తెలుగు (Telugu)":     ("telugu",    "te"),
    "🇮🇳 ಕನ್ನಡ (Kannada)":     ("kannada",   "kn"),
    "🇮🇳 മലയാളം (Malayalam)":  ("malayalam", "ml"),
    "🇮🇳 বাংলা (Bengali)":     ("bengali",   "bn"),
    "🇮🇳 मराठी (Marathi)":     ("marathi",   "mr"),
    "🇮🇳 ગુજરાતી (Gujarati)":  ("gujarati",  "gu"),
}

EXAMPLES = [
    "Which fertilizer is best for wheat?",
    "How to treat pest attack on tomato?",
    "Best crops for black soil?",
    "What is PM-Kisan scheme?",
    "How to improve soil fertility organically?",
    "How to control fungal disease in crops?",
    "When to irrigate paddy crop?",
    "What is MSP for rice?",
]


# ── API helpers ───────────────────────────────────────────────────────────────

def get_health() -> dict:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline", "vector_store_ready": False,
            "api_key_configured": False,
            "issues": ["Backend not running on port 8000"],
        }
    except Exception as e:
        return {"status": "error", "vector_store_ready": False,
                "api_key_configured": False, "issues": [str(e)]}


def check_ollama() -> dict:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            return {"running": True, "models": models}
        return {"running": False, "models": []}
    except Exception:
        return {"running": False, "models": []}


def validate_ollama() -> dict:
    try:
        r = requests.get(f"{API_BASE}/validate-key", timeout=30)
        return r.json()
    except Exception as e:
        return {"valid": False, "message": f"Cannot reach backend: {e}"}


def ask_api(query: str, language: str, city, top_k: int) -> dict | None:
    try:
        r = requests.post(
            f"{API_BASE}/ask",
            json={"query": query, "language": language,
                  "city": city, "top_k": top_k},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend offline. Run: `uvicorn app.main:app --reload --port 8000`")
    except requests.exceptions.Timeout:
        st.error("⏱️ llama3 timed out. Model may be loading — wait 30s and retry.")
    except requests.exceptions.HTTPError:
        try:    detail = r.json().get("detail", r.text)
        except: detail = r.text
        st.error(f"❌ API Error: {detail}")
    except Exception as e:
        st.error(f"❌ {e}")
    return None


def get_tts(text: str, lang: str) -> bytes | None:
    """Call TTS endpoint — returns None gracefully on any error."""
    try:
        r = requests.post(
            f"{API_BASE}/voice/speak",
            data={"text": text[:500], "lang": lang},   # limit length
            timeout=30,
        )
        if r.status_code == 404:
            st.warning("⚠️ TTS endpoint not found. Make sure voice.py is in app/routes/ and restart backend.")
            return None
        r.raise_for_status()
        return r.content
    except requests.exceptions.HTTPError as e:
        st.warning(f"⚠️ TTS unavailable: {e}")
        return None
    except Exception as e:
        st.warning(f"⚠️ TTS failed: {e}")
        return None


def transcribe_audio(audio_bytes: bytes, suffix: str) -> str | None:
    try:
        r = requests.post(
            f"{API_BASE}/voice/transcribe",
            files={"file": (f"audio{suffix}", audio_bytes, "audio/wav")},
            timeout=90,
        )
        r.raise_for_status()
        return r.json().get("text", "")
    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        return None


# ── Session state ─────────────────────────────────────────────────────────────
if "history"      not in st.session_state: st.session_state.history      = []
if "prefill"      not in st.session_state: st.session_state.prefill      = ""
if "health_cache" not in st.session_state: st.session_state.health_cache = get_health()
if "ollama_cache" not in st.session_state: st.session_state.ollama_cache = check_ollama()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 Rural AI Assistant")
    st.caption("🦙 **Ollama llama3** — 100% Free & Local")
    st.divider()

    lang_label           = st.selectbox("🌐 Response Language", list(LANGUAGES.keys()))
    lang_name, lang_code = LANGUAGES[lang_label]
    city_input           = st.text_input("📍 City (for weather)", placeholder="e.g. Nagpur")

    with st.expander("⚙️ Settings"):
        top_k      = st.slider("Context chunks", 1, 10, 4)
        enable_tts = st.toggle("🔊 Read answer aloud", value=False)

    st.divider()
    st.markdown("### 🔌 System Status")

    if st.button("🔄 Refresh Status", use_container_width=True):
        st.session_state.health_cache = get_health()
        st.session_state.ollama_cache = check_ollama()

    h      = st.session_state.health_cache
    ollama = st.session_state.ollama_cache

    # Backend
    if h.get("status") == "offline":
        st.error("❌ Backend OFFLINE")
        st.code("uvicorn app.main:app --reload --port 8000")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Backend",   "✅ ON")
        c2.metric("Vector DB", "✅" if h.get("vector_store_ready") else "❌")
        if not h.get("vector_store_ready"):
            st.warning("⚠️ Vector store missing")
            st.code("python scripts/ingest_data.py")

    # Ollama
    st.markdown("**🦙 Ollama**")
    if ollama.get("running"):
        st.success("✅ Running")
        for m in ollama.get("models", []):
            st.caption(f"  • {m}")
        if not ollama.get("models"):
            st.warning("No models pulled")
            st.code("ollama pull llama3")
    else:
        st.error("❌ NOT Running")
        with st.expander("How to start"):
            st.code("ollama run llama3")

    if st.button("🧪 Test Ollama", use_container_width=True):
        with st.spinner("Testing ..."):
            res = validate_ollama()
        if res.get("valid"):
            st.success(res["message"])
        else:
            st.error(res["message"])

    st.divider()
    st.caption("🦙 llama3 · 🗄️ FAISS · 🎤 Whisper · 🌐 deep-translator")


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("<div style='font-size:3rem;margin-top:8px'>🌾</div>",
                unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin:0;color:#1b5e20;'>Rural AI Assistant</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#555;margin:0;'>Ask about "
        "<b>crops, soil, pests, schemes & weather</b> "
        "in your language — powered by 🦙 Ollama llama3</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Warning banners
h      = st.session_state.health_cache
ollama = st.session_state.ollama_cache

if h.get("status") == "offline":
    st.error("🔴 **Backend OFFLINE** → open terminal: `uvicorn app.main:app --reload --port 8000`")
elif not ollama.get("running"):
    st.warning(
        "🦙 **Ollama is not running!** — open terminal and run: `ollama run llama3`  \n"
        "First time? Download: https://ollama.com/download",
        icon="⚠️",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_ask, tab_voice, tab_hist, tab_guide = st.tabs([
    "💬 Ask a Question",
    "🎤 Voice Query",
    "📜 History",
    "🛠️ Setup Guide",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ASK
# ─────────────────────────────────────────────────────────────────────────────
with tab_ask:
    col_input, col_examples = st.columns([3, 1])

    with col_examples:
        st.markdown('<div class="section-header">📋 Examples</div>', unsafe_allow_html=True)
        for i, ex in enumerate(EXAMPLES):
            label = ex if len(ex) <= 36 else ex[:36] + "…"
            if st.button(label, key=f"ex_{i}", use_container_width=True):
                st.session_state.prefill = ex
                st.rerun()

    with col_input:
        query = st.text_area(
            "✍️ Your Question",
            value       = st.session_state.prefill,
            placeholder = "e.g. Which fertilizer is best for wheat in black soil?",
            height      = 140,
        )
        if st.session_state.prefill and query == st.session_state.prefill:
            st.session_state.prefill = ""

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            ask_btn = st.button(
                "🔍 Ask llama3",
                type             = "primary",
                use_container_width = True,
            )
        with col_btn2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
            if clear_btn:
                st.session_state.prefill = ""
                st.rerun()

    # ── Process query ─────────────────────────────────────────────────────────
    if ask_btn:
        if not query.strip():
            st.warning("⚠️ Please type a question first.")
        elif not ollama.get("running"):
            st.error("🦙 Ollama not running. Open terminal → `ollama run llama3`")
        else:
            with st.spinner("🦙 llama3 thinking … (first query may take 30 seconds)"):
                result = ask_api(
                    query.strip(), lang_name,
                    city_input.strip() or None, top_k,
                )

            if result:
                answer = result["answer"]

                # Save to history
                st.session_state.history.append({
                    "query":   query,
                    "answer":  answer,
                    "sources": result.get("sources", []),
                    "intent":  result.get("intent_label", ""),
                    "chunks":  result.get("chunks_used", 0),
                })

                # ── Intent + stats row ────────────────────────────────────────
                intent_label = result.get("intent_label", "💬 General Query")
                sources      = result.get("sources", [])
                chunks_used  = result.get("chunks_used", 0)

                st.markdown(
                    f'<span class="intent-badge">🎯 {intent_label}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="stat-row">'
                    f'<div class="stat-card">📄 {len(sources)} Source File(s)</div>'
                    f'<div class="stat-card">🔍 {chunks_used} Chunks Used</div>'
                    f'<div class="stat-card">🌐 {lang_label.split()[1] if len(lang_label.split())>1 else "English"}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # ── Weather block ─────────────────────────────────────────────
                w = result.get("weather")
                if w and "error" not in w:
                    st.markdown(
                        f'<div class="weather-box">{w.get("summary","")}</div>',
                        unsafe_allow_html=True,
                    )
                elif w and "error" in w:
                    st.warning(f"Weather: {w['error']}")

                # ── Answer box — guaranteed visible text ──────────────────────
                st.markdown(
                    '<div class="section-header">📢 Answer</div>',
                    unsafe_allow_html=True,
                )

                is_err = answer.startswith(("❌", "⚠️"))

                if is_err:
                    # Error shown in orange box with clear text
                    safe_answer = answer.replace("\n", "<br>").replace("'", "&#39;")
                    st.markdown(
                        f'<div class="error-box">{safe_answer}</div>',
                        unsafe_allow_html=True,
                    )
                    if "ollama" in answer.lower():
                        st.info(
                            "**Quick Fix:**\n"
                            "1. Download → https://ollama.com/download\n"
                            "2. Run: `ollama run llama3`\n"
                            "3. Wait for download (~4.7GB), then retry."
                        )
                else:
                    # Answer in white card with FORCED dark text
                    # Replace newlines with <br> for HTML rendering
                    safe_answer = (
                        answer
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                        .replace("'", "&#39;")
                    )
                    st.markdown(
                        f'<div class="answer-card">'
                        f'<p style="color:#1a1a1a !important;margin:0;">{safe_answer}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # ── Sources ───────────────────────────────────────────────────
                if sources:
                    st.markdown(
                        "**📚 Sources:** " +
                        " ".join(
                            f'<span class="source-tag">📄 {s}</span>'
                            for s in sources
                        ),
                        unsafe_allow_html=True,
                    )

                # ── TTS ───────────────────────────────────────────────────────
                if enable_tts and not is_err:
                    with st.spinner("🔊 Generating audio …"):
                        audio = get_tts(answer, lang_code)
                    if audio:
                        st.audio(audio, format="audio/mp3")

                # ── Feedback ──────────────────────────────────────────────────
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                c1.button("👍 Helpful",      key="fb_good",  use_container_width=True)
                c2.button("👎 Not helpful",  key="fb_bad",   use_container_width=True)
                c3.button("🔁 Ask another",  key="fb_retry", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — VOICE
# ─────────────────────────────────────────────────────────────────────────────
with tab_voice:
    st.markdown('<div class="section-header">🎤 Ask with Your Voice</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="answer-card" style="border-left-color:#1976d2;">'
        '🎙️ Upload a .wav or .mp3 file. '
        '<b>Whisper + llama3 both run locally</b> — fully private, no cloud.'
        '</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload audio file",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
    )

    if uploaded:
        st.audio(uploaded)
        if st.button("🎤 Transcribe & Ask llama3", type="primary",
                     use_container_width=True):
            data   = uploaded.read()
            suffix = ("." + uploaded.name.rsplit(".", 1)[-1]
                      if "." in uploaded.name else ".wav")

            with st.spinner("🎤 Transcribing with Whisper …"):
                text = transcribe_audio(data, suffix)

            if text:
                st.success(f"**Heard:** {text}")
                with st.spinner("🦙 llama3 answering …"):
                    result = ask_api(
                        text, lang_name,
                        city_input.strip() or None, top_k,
                    )
                if result:
                    answer = result["answer"]
                    safe_answer = (
                        answer
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )
                    st.markdown(
                        f'<div class="answer-card">'
                        f'<p style="color:#1a1a1a !important;margin:0;">{safe_answer}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if result.get("sources"):
                        st.markdown(
                            "**Sources:** " +
                            " ".join(f'<span class="source-tag">{s}</span>'
                                     for s in result["sources"]),
                            unsafe_allow_html=True,
                        )
                    if enable_tts:
                        audio = get_tts(answer, lang_code)
                        if audio:
                            st.audio(audio, format="audio/mp3")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — HISTORY
# ─────────────────────────────────────────────────────────────────────────────
with tab_hist:
    st.markdown('<div class="section-header">📜 Session History</div>',
                unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No questions asked yet in this session.")
    else:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.history)):
            n = len(st.session_state.history) - i
            with st.expander(f"Q{n}: {item['query'][:70]}"):
                if item.get("intent"):
                    st.markdown(
                        f'<span class="intent-badge">{item["intent"]}</span>',
                        unsafe_allow_html=True,
                    )
                st.markdown(f"**Question:** {item['query']}")

                safe = (
                    item["answer"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>")
                )
                st.markdown(
                    f'<div class="answer-card" style="margin-top:8px;">'
                    f'<p style="color:#1a1a1a !important;margin:0;">{safe}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if item.get("sources"):
                    st.caption(f"📄 Sources: {', '.join(item['sources'])}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — SETUP GUIDE
# ─────────────────────────────────────────────────────────────────────────────
with tab_guide:
    st.markdown('<div class="section-header">🛠️ Setup Guide</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="answer-card" style="border-left-color:#388e3c;">'
        '✅ <b>100% FREE. No API key. No credit card. '
        'Runs entirely on your PC.</b>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Step 1 — Install Ollama")
    st.markdown("Download from **https://ollama.com/download** and install.")

    st.markdown("#### Step 2 — Pull llama3 model (~4.7GB, one time)")
    st.code("ollama run llama3", language="bash")

    st.markdown("#### Step 3 — Create `.env` file in project root")
    st.code(
        "OLLAMA_MODEL=llama3\n"
        "OLLAMA_BASE_URL=http://localhost:11434\n"
        "LLM_MAX_TOKENS=512\n"
        "LLM_TEMPERATURE=0.3\n"
        "WHISPER_MODEL=base\n"
        "TOP_K_RESULTS=4",
        language="bash",
    )

    st.markdown("#### Step 4 — Build vector store")
    st.code("python scripts/ingest_data.py", language="bash")

    st.markdown("#### Step 5 — Start both servers")
    st.code(
        "# Terminal 1:\nuvicorn app.main:app --reload --port 8000\n\n"
        "# Terminal 2:\nstreamlit run frontend/app.py",
        language="bash",
    )

    st.markdown("#### Error Reference")
    st.markdown("""
| Error | Cause | Fix |
|---|---|---|
| Answer text invisible | CSS conflict | ✅ Fixed in this version |
| TTS 404 error | voice.py missing or wrong route | ✅ Replace voice.py + main.py |
| Ollama NOT Running | Ollama not started | `ollama run llama3` |
| Vector store missing | ingest not run | `python scripts/ingest_data.py` |
| Backend OFFLINE | FastAPI not started | `uvicorn app.main:app --reload` |
| Timed out | Model loading into RAM | Wait 30s and retry |
""")