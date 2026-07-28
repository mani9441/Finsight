# FinSight — Financial Analytics & Sentiment Advisory

FinSight is a professional financial intelligence dashboard that integrates multi-source financial metrics, news sentiment analytics, and AI-driven advisory capabilities.

## Phase 1 — Project Foundation

This phase establishes the technical foundation, environment, logging, custom configuration loaders, and error-handling framework required for all subsequent features.

### Project Structure

```text
FinSight/
│
├── app.py                  # Main entry point (Streamlit application)
├── requirements.txt        # Python dependency manifest
├── README.md               # Setup and architecture documentation
├── .env                    # Local environment secrets and settings (gitignored)
├── .gitignore              # Files/folders to exclude from version control
│
├── config/
│   ├── __init__.py         # Exposes Configuration Singleton
│   └── settings.py         # Config loader & environment variables parser
│
├── core/
│   ├── __init__.py         # Core infrastructure package definition
│   ├── exceptions.py       # Centrally defined custom exceptions
│   ├── logger.py           # Multi-handler logging infrastructure (console + file)
│   └── constants.py        # Global constants and metadata configuration
│
├── services/               # Future external API services (yfinance, NLP, OpenAI)
│   └── __init__.py
│
├── models/                 # Future structured financial/sentiment data models
│   └── __init__.py
│
├── components/             # Reusable UI component modules
│   └── __init__.py
│
├── pages/                  # Future subpages for multi-page dashboard setups
│
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Math, date, and general layout formatting helpers
│
├── assets/
│   ├── images/             # Static visual assets
│   ├── icons/              # Static custom UI icons
│   └── styles/
│       └── main.css        # Custom premium CSS theme styling
│
├── data/                   # Gitignored local/cache databases
└── logs/                   # Application logs directory
```

---

## Setup & Running Guide

### 1. Prerequisites
- Python 3.12 or higher
- Git
- Conda package manager

### 2. Environment Activation & Dependencies Installation
To run this application in the conda environment `finsight`, activate it and run pip install:
```bash
conda activate finsight
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (based on the template settings inside `.env` or settings.py):
```env
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO
OPENAI_API_KEY=your_key_here
```

### 4. Running the Streamlit App
Run the following command from the root of the project:
```bash
streamlit run app.py
```

### 5. Logs Inspection
Operational logs are outputted to the console and written to `logs/finsight.log` in real-time.
