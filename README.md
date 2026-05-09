# 🔍 Fact-Check Agent

> AI-powered truth layer for marketing and business documents.  
> Upload a PDF → extract factual claims → verify against live web data → get a structured report.

![Fact-Check Agent Demo](assets/demo_video.mp4)

**Live App:** [https://your-app.streamlit.app](https://your-app.streamlit.app) *(replace after deployment)*

---

## Features

| Feature | Details |
|---|---|
| 📄 PDF Upload | Drag-and-drop or browse; up to 50 MB |
| 🤖 AI Claim Extraction | GPT-4.1-mini identifies only measurable factual claims |
| 🌐 Live Web Search | Tavily retrieves top 5 sources per claim |
| ✅ Automated Verification | Claims classified as Verified / Inaccurate / False / Not Enough Evidence |
| 📊 Results Dashboard | Color-coded verdicts, corrected facts, explanations, source links |
| ⬇️ Downloadable Reports | Export as CSV or JSON |
| ⚡ Parallel Processing | ThreadPoolExecutor for fast multi-claim verification |
| 💾 Search Caching | Avoids duplicate API calls within a session |

---

## Local Setup

### Prerequisites
- Python 3.10+
- OpenAI API key ([platform.openai.com](https://platform.openai.com))
- Tavily API key ([tavily.com](https://tavily.com))

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/fact-check-agent.git
cd fact-check-agent

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
#    Edit .streamlit/secrets.toml — already created from the template:
nano .streamlit/secrets.toml
```

**`.streamlit/secrets.toml`:**
```toml
OPENAI_API_KEY = "sk-..."
TAVILY_API_KEY = "tvly-..."
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
fact-check-agent/
│
├── app.py                    # Main Streamlit application
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   ├── secrets.toml          # API keys (not committed)
│   └── config.toml           # Theme & server settings
│
├── utils/
│   ├── __init__.py
│   ├── pdf_extractor.py      # PyMuPDF text extraction
│   ├── claim_extractor.py    # OpenAI claim identification
│   ├── web_search.py         # Tavily web search + caching
│   ├── verifier.py           # OpenAI claim verification
│   ├── report_generator.py   # CSV / JSON export
│   └── helpers.py            # Shared utilities
│
├── sample_pdfs/              # Place test PDFs here
└── assets/
    └── demo_video.mp4
```

---

## Deployment on Streamlit Community Cloud

1. Push your repository to GitHub (ensure `secrets.toml` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repository and set **Main file path** to `app.py`.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   OPENAI_API_KEY = "sk-..."
   TAVILY_API_KEY = "tvly-..."
   ```
5. Click **Deploy**.

---

## Cost Estimation

| Operation | Model | Cost per claim (est.) |
|---|---|---|
| Claim extraction | gpt-4.1-mini | ~$0.001 (one-time per doc) |
| Web search | Tavily | ~$0.005 per query |
| Verification | gpt-4.1-mini | ~$0.002 per claim |

For a 20-claim document: **≈ $0.15–0.20 total**.

---

## Configuration

| Setting | Location | Default |
|---|---|---|
| Max claims per doc | `app.py → MAX_CLAIMS` | 20 |
| Parallel workers | `app.py → MAX_WORKERS` | 5 |
| Max text sent to AI | `claim_extractor.py → max_chars` | 12,000 |
| Search results per claim | `web_search.py → max_results` | 5 |

---

## License

MIT © 2024 — feel free to use, modify, and deploy.
