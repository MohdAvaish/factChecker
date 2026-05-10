# 🔍 Fact-Check Agent

> AI-powered truth layer for PDFs, marketing decks, whitepapers, and business documents.  
> Upload a PDF → extract factual claims → verify against live web data → generate downloadable reports.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 PDF Upload | Upload research papers, reports, pitch decks, and whitepapers |
| 🤖 AI Claim Extraction | DeepSeek V3 extracts measurable factual claims only |
| 🌐 Live Web Verification | Tavily performs real-time web search for evidence |
| ✅ Intelligent Fact Checking | Claims classified as Verified / Inaccurate / False / Not Enough Evidence |
| 📊 Interactive Dashboard | Modern cyberpunk UI with verdict analytics |
| 🧠 Corrected Facts | Provides corrected real-world information for inaccurate claims |
| 🔗 Source Attribution | Displays supporting evidence links |
| ⚡ Parallel Verification | Multi-threaded verification for faster processing |
| ⬇️ Export Reports | Download reports as CSV, JSON, and Styled PDF |
| 🎨 Premium UI | Futuristic dark-themed Streamlit interface |

---

# 🖥️ Live Demo

**Live App:**  
https://your-app.streamlit.app

> Replace with your deployed Streamlit URL.

---

# 📸 Screenshots

## Upload Interface

Add screenshot here:

```text
assets/upload_ui.png
```

## Verification Dashboard

```text
assets/dashboard.png
```

## PDF Report

```text
assets/pdf_report.png
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Models | DeepSeek V3 |
| Web Search | Tavily API |
| PDF Parsing | PyMuPDF |
| Report Export | Pandas + ReportLab |
| Concurrency | ThreadPoolExecutor |

---

# 📂 Project Structure

```bash
fact-check-agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   ├── secrets.toml
│   └── config.toml
│
├── utils/
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── claim_extractor.py
│   ├── verifier.py
│   ├── web_search.py
│   ├── report_generator.py
│   └── helpers.py
│
├── assets/
│   ├── dashboard.png
│   ├── upload_ui.png
│   ├── pdf_report.png
│   └── demo_video.mp4
│
└── sample_pdfs/
```

---

# ⚙️ Local Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/fact-check-agent.git

cd fact-check-agent
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Keys Setup

Create:

```bash
.streamlit/secrets.toml
```

Add:

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# ☁️ Streamlit Cloud Deployment

## Step 1 — Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push
```

---

## Step 2 — Deploy

Go to:

https://share.streamlit.io

Create a new app and select:

- Repository
- Branch
- `app.py`

---

## Step 3 — Add Secrets

In Streamlit Cloud:

### Advanced Settings → Secrets

Paste:

```toml
DEEPSEEK_API_KEY = "your_key"
TAVILY_API_KEY = "your_key"
```

---

# 📊 Verdict Categories

| Verdict | Meaning |
|---|---|
| ✅ Verified | Claim matches credible sources |
| ⚠️ Inaccurate | Claim partially correct but outdated/wrong |
| ❌ False | Claim contradicted by evidence |
| 🔵 Not Enough Evidence | Insufficient trustworthy information |

---

# 📥 Export Options

The app supports downloading:

- CSV Report
- JSON Report
- Styled PDF Report

The PDF report includes:

- Verdict summaries
- Corrected facts
- Evidence links
- Professional formatting

---

# ⚡ Performance

| Setting | Default |
|---|---|
| Max Claims | 20 |
| Parallel Workers | 5 |
| Max Text Length | 12,000 chars |
| Search Results per Claim | 5 |

---

# 💰 Estimated API Cost

| Operation | Cost |
|---|---|
| Claim Extraction | ~$0.001 per document |
| Tavily Search | ~$0.005/query |
| Verification | ~$0.002/claim |

Typical 20-claim PDF:

```text
≈ $0.10 – $0.20 total
```

---

# 🧪 Testing the System

Use PDFs containing:

- Fake statistics
- Outdated market numbers
- Incorrect years
- Wrong technical specs

The app should:

✅ Detect inaccuracies  
✅ Provide corrected facts  
✅ Link evidence sources

---

# 🚀 Future Improvements

- OCR support for scanned PDFs
- Multi-language fact checking
- Hallucination confidence score
- Citation reliability ranking
- AI-generated summary reports
- Authentication & user history
- Vector database memory

---

# 📜 License

MIT License © 2026

Free to use, modify, and deploy.

---

# 👨‍💻 Author

Developed by Mohammad Ayan Siddiqui

Built with:
- Streamlit
- DeepSeek
- Tavily
- Python
