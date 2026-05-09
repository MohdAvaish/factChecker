"""
Fact-Check Agent - Main Streamlit Application
Automated fact-checking for PDF documents using AI and live web search.
"""

import streamlit as st
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from utils.pdf_extractor import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.web_search import search_web
from utils.verifier import verify_claim
from utils.helpers import get_verdict_config, truncate_text
from utils.report_generator import (
    generate_csv,
    generate_json,
    generate_pdf
)
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Background ── */
  .stApp {
    background: #0a0a0f;
    color: #e8e8f0;
  }

  /* ── Hero header ── */
  .hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
  }
  .hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #6c6c8a;
    margin-bottom: 0.75rem;
  }
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 1rem;
  }
  .hero-sub {
    font-size: 1.05rem;
    color: #7c7c9a;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
  }

  /* ── Upload zone ── */
  [data-testid="stFileUploader"] {
    background: #12121c !important;
    border: 1.5px dashed #2e2e45 !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: border-color 0.2s;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: #7c3aed !important;
  }

  /* ── Verdict badges ── */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .badge-verified   { background: #052e16; color: #4ade80; border: 1px solid #166534; }
  .badge-inaccurate { background: #422006; color: #fbbf24; border: 1px solid #92400e; }
  .badge-false      { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
  .badge-nee        { background: #0c1445; color: #60a5fa; border: 1px solid #1e3a8a; }

  /* ── Claim card ── */
  .claim-text {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #c4c4d8;
    background: #0e0e18;
    border-left: 3px solid #3a3a55;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1rem;
  }
  .fact-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #5a5a78;
    margin-bottom: 0.3rem;
  }
  .correct-fact {
    font-size: 0.95rem;
    color: #e8e8f0;
    background: #13131f;
    padding: 0.6rem 0.9rem;
    border-radius: 8px;
    margin-bottom: 0.75rem;
  }
  .explanation {
    font-size: 0.88rem;
    color: #8888aa;
    line-height: 1.6;
    margin-bottom: 0.75rem;
  }
  .source-chip {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #7c3aed;
    background: #1a1030;
    border: 1px solid #2e1a5e;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 3px 3px 3px 0;
    text-decoration: none;
    transition: background 0.15s;
  }
  .source-chip:hover { background: #2a1f50; }

  /* ── Stat cards ── */
  .stat-row {
    display: flex;
    gap: 12px;
    margin: 1.5rem 0;
  }
  .stat-card {
    flex: 1;
    background: #11111b;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
  }
  .stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
  }
  .stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #5a5a78;
  }

  /* ── Section divider ── */
  .section-divider {
    border: none;
    border-top: 1px solid #1a1a2e;
    margin: 2rem 0;
  }

  /* ── Progress label ── */
  .progress-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #5a5a78;
    margin-bottom: 4px;
  }

  /* ── Streamlit overrides ── */
  .stExpander {
    background: #11111b !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
  }
  .stExpander > div > div > div > div {
    color: #e8e8f0 !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }
  .stDownloadButton > button {
    background: #13131f !important;
    color: #a78bfa !important;
    border: 1px solid #2e2e45 !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
  }
  [data-testid="stMarkdownContainer"] p { color: #c4c4d8; }
</style>
""", unsafe_allow_html=True)

MAX_CLAIMS = 20
MAX_WORKERS = 5


# ── Helpers ───────────────────────────────────────────────────────────────────

def process_single_claim(claim: str, idx: int) -> Dict[str, Any]:
    """Search and verify one claim; returns enriched result dict."""
    search_results = search_web(claim)
    result = verify_claim(claim, search_results)
    result["claim"] = claim
    result["index"] = idx
    return result


# ── Session state init ─────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = []
if "claims" not in st.session_state:
    st.session_state.claims = []


# ── UI ────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-Powered Document Analysis</div>
  <div class="hero-title">Fact-Check Agent</div>
  <div class="hero-sub">Upload any PDF and instantly verify every factual claim against live web sources.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Upload
col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Supports marketing decks, research reports, whitepapers, and business documents.",
    )

with col_info:
    st.markdown("""
    <div style="padding: 1rem; background: #11111b; border-radius: 12px; border: 1px solid #1e1e2e;">
      <div class="fact-label" style="margin-bottom: 0.6rem;">What gets checked</div>
      <div style="font-size: 0.85rem; color: #7c7c9a; line-height: 1.8;">
        📊 Statistics &amp; percentages<br>
        📅 Dates &amp; timelines<br>
        💰 Financial figures<br>
        👥 User &amp; market counts<br>
        📐 Technical measurements
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Processing pipeline ────────────────────────────────────────────────────────

if uploaded_file and st.button("🔍  Analyze Document", use_container_width=False):
    st.session_state.results = []
    st.session_state.claims = []

    with st.status("Processing document…", expanded=True) as status:

        # Step 1 – Extract text
        st.write("📄 Extracting text from PDF…")
        try:
            raw_text = extract_text_from_pdf(uploaded_file)
            if not raw_text.strip():
                st.error("Could not extract text. Is this a scanned/image-only PDF?")
                st.stop()
            st.write(f"✅ Extracted **{len(raw_text):,}** characters.")
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")
            st.stop()

        # Step 2 – Extract claims
        st.write("🤖 Identifying factual claims with AI…")
        try:
            claims = extract_claims(raw_text)
            claims = claims[:MAX_CLAIMS]
            st.session_state.claims = claims
            st.write(f"✅ Found **{len(claims)}** verifiable claims.")
        except Exception as e:
            st.error(f"Claim extraction failed: {e}")
            st.stop()

        if not claims:
            st.warning("No verifiable factual claims found in this document.")
            status.update(label="Done — no claims found.", state="complete")
            st.stop()

        # Step 3 – Parallel verify
        st.write(f"🌐 Searching the web and verifying {len(claims)} claims in parallel…")
        results: List[Dict[str, Any]] = [None] * len(claims)
        progress_bar = st.progress(0)
        completed = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_idx = {
                executor.submit(process_single_claim, claim, i): i
                for i, claim in enumerate(claims)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as exc:
                    results[idx] = {
                        "claim": claims[idx],
                        "index": idx,
                        "status": "Not Enough Evidence",
                        "correct_fact": "Unable to retrieve.",
                        "explanation": f"Error during verification: {exc}",
                        "sources": [],
                    }
                completed += 1
                progress_bar.progress(completed / len(claims))

        st.session_state.results = [r for r in results if r is not None]
        status.update(label="✅ Analysis complete!", state="complete")

# ── Results dashboard ──────────────────────────────────────────────────────────

if st.session_state.results:
    results = st.session_state.results

    # Summary stats
    counts = {"Verified": 0, "Inaccurate": 0, "False": 0, "Not Enough Evidence": 0}
    for r in results:
        s = r.get("status", "Not Enough Evidence")
        counts[s] = counts.get(s, 0) + 1

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem;">
      Results Overview
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-num" style="color: #4ade80">{counts['Verified']}</div>
        <div class="stat-label">Verified</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color: #fbbf24">{counts['Inaccurate']}</div>
        <div class="stat-label">Inaccurate</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color: #f87171">{counts['False']}</div>
        <div class="stat-label">False</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color: #60a5fa">{counts['Not Enough Evidence']}</div>
        <div class="stat-label">Unverified</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color: #a78bfa">{len(results)}</div>
        <div class="stat-label">Total Claims</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem;">
      Claim-by-Claim Analysis
    </div>
    """, unsafe_allow_html=True)

    for r in results:
        cfg = get_verdict_config(r.get("status", "Not Enough Evidence"))
        label = f"{cfg['icon']}  Claim {r['index'] + 1} — {r.get('status', 'Unknown')}"

        with st.expander(label):
            # Claim text
            claim_display = truncate_text(r['claim'], 300)
            st.markdown(f"<div class='claim-text'>\u201c{claim_display}\u201d</div>", unsafe_allow_html=True)

            # Badge
            st.markdown(f"<span class='badge {cfg['badge_class']}'>{cfg['icon']} {r.get('status', 'Unknown')}</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("<div class='fact-label'>Correct Fact</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='correct-fact'>{r.get('correct_fact', '—')}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='fact-label'>Explanation</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='explanation'>{r.get('explanation', '—')}</div>", unsafe_allow_html=True)

            # Sources
            sources = r.get("sources", [])
            if sources:
                st.markdown("<div class='fact-label'>Sources</div>", unsafe_allow_html=True)
                chips_html = " ".join(
                    f"<a class='source-chip' href='{url}' target='_blank' rel='noopener noreferrer'>"
                    f"🔗 Source {i+1}</a>"
                    for i, url in enumerate(sources) if url
                )
                st.markdown(chips_html, unsafe_allow_html=True)

   # ── Download reports ────────────────────────────────────────

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

st.markdown("""
<div style="font-family: 'Syne', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1rem;">
  Download Report
</div>
""", unsafe_allow_html=True)

dcol1, dcol2, dcol3 = st.columns([1, 1, 1])

with dcol1:
    csv_data = generate_csv(st.session_state.results)

    st.download_button(
        label="⬇ Download CSV",
        data=csv_data,
        file_name="fact_check_report.csv",
        mime="text/csv",
        use_container_width=True,
    )

with dcol2:
    json_data = generate_json(st.session_state.results)

    st.download_button(
        label="⬇ Download JSON",
        data=json_data,
        file_name="fact_check_report.json",
        mime="application/json",
        use_container_width=True,
    )

with dcol3:
    pdf_data = generate_pdf(st.session_state.results)

    st.download_button(
        label="⬇ Download PDF",
        data=pdf_data,
        file_name="fact_check_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-family: 'DM Mono', monospace; font-size: 0.68rem;
            color: #3a3a55; padding-bottom: 2rem;">
  Fact-Check Agent · Powered by OpenAI &amp; Tavily · Built with Streamlit
</div>
""", unsafe_allow_html=True)
