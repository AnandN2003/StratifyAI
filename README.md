## StratifyAI - Autonomous Company Research Agent

[![Python](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-brightgreen.svg)](https://www.docker.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-orchestration-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-purple.svg)](https://ai.google.dev/)

> **An intelligent AI agent that autonomously researches companies, detects conflicting information, and generates professional account plans for sales due diligence.**

---

## 📖 Overview

StratifyAI is an **Agentic AI system** built with LangGraph that combines web search, LLM-powered analysis, and human-in-the-loop decision making to create comprehensive company research reports. Perfect for sales teams, investors, and business analysts who need fast, reliable company intelligence.

### Key Features

- **Autonomous Web Research** - Searches 12+ sources per company using Tavily API
- **AI-Powered Conflict Detection** - Gemini 2.5 Flash identifies factual discrepancies
- **Human-in-the-Loop** - Interactive prompts for critical decisions when conflicts arise
- **Structured Account Plans** - Professional reports with SWOT analysis and sales insights
- **Fully Dockerized** - Reproducible environment, runs anywhere
- **Fast Execution** - Complete research and report in 30-45 seconds

---

## Architecture

```
User Input → Researcher → Reviewer → [Human Review?] → Writer → Account Plan
              (Tavily)    (Gemini)    (Interactive)    (Gemini)
```

**4-Node LangGraph Workflow:**
1. **Researcher Node** - 4 targeted web searches (12 sources total)
2. **Reviewer Node** - AI fact-checking for conflicts
3. **Human Node** - Interactive decision making when needed
4. **Writer Node** - Professional report generation


## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- API keys for Gemini and Tavily (in `.env` file)

### Running the Application

1. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Open your browser and navigate to: `http://localhost:8501`
   - You'll see the landing page
   - Click "Get Started" to access the chat interface

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 📁 Project Structure

```
StratifyAI/
├── app/                        # Streamlit application
│   ├── landing.py              # Landing page (main entry point)
│   ├── streamlit_app.py        # Original research interface
│   ├── streamlit_chat.py       # Alternative chat interface
│   ├── .streamlit/
│   │   └── config.toml         # Streamlit configuration
│   └── pages/
│       └── chat.py             # Chat interface page
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main App component
│   │   ├── Chat.jsx            # Chat interface component
│   │   ├── Landing.jsx         # Landing page component
│   │   ├── main.jsx            # React entry point
│   │   ├── App.css             # App styles
│   │   ├── Chat.css            # Chat styles
│   │   └── index.css           # Global styles
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── Dockerfile              # Frontend Docker configuration
│   ├── nginx.conf              # Nginx configuration
│   └── vite.config.js          # Vite bundler configuration
├── src/                        # Core AI agent logic
│   ├── graph.py                # LangGraph agent workflow
│   ├── entrypoint.py           # CLI entry point
│   └── __init__.py             # Package initialization
├── backend_api.py              # Flask API backend
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Backend Docker configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

## Features

- **AI-Powered Research**: Leverages advanced AI to analyze companies instantly
- **Comprehensive Account Plans**: Generates detailed plans with key insights
- **Lightning Fast**: Get results in minutes instead of hours
- **Smart Targeting**: Identify decision-makers and organizational structure
- **Strategic Insights**: Uncover growth initiatives and strategic priorities
- **Conversational Interface**: Natural chat-based interaction
- **Export Options**: Download reports as Markdown or PDF

## 🔧 Configuration

The application is configured through environment variables in the `.env` file:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `TAVILY_API_KEY`: Your Tavily search API key

## 📝 Usage

1. Start on the landing page
2. Click "Get Started" to access the chat
3. Enter a company name to research
4. Review the AI-generated account plan
5. Download the report in your preferred format (MD or PDF)

---
## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | LangGraph | State management & workflow routing |
| **LLM** | Google Gemini 2.5 Flash | Analysis & report generation |
| **Search** | Tavily API | Web research (12 sources/company) |
| **Backend** | Python 3.9 | Core logic |
| **Container** | Docker | Reproducible environment |
| **Framework** | LangChain | LLM integration |

---

## Use Cases

- **Sales Teams** - Pre-call research and account planning
- **Investment Analysts** - Company due diligence
- **Business Development** - Partner evaluation
- **Consultants** - Client background research
- **Market Research** - Competitive intelligence

---

## 🎬 How It Works

### 1. Research Phase
The **Researcher Node** executes 4 targeted queries:
- Company overview and business model
- Recent news and developments
- Products and services
- Market position and competitors

Each query returns 3 sources = **12 total web articles**

### 2. Conflict Detection
The **Reviewer Node** sends all findings to Gemini AI:
- Checks for numerical discrepancies (revenue, employees)
- Identifies conflicting facts (CEO names, headquarters)
- Detects mixed company identities (same acronym)
- Returns structured JSON with conflict status

### 3. Human Decision (If Needed)
When conflicts detected:
```
⚠️ CONFLICT DETECTED - HUMAN REVIEW REQUIRED

Finding 2 lists headquarters as "Dublin, Ireland, UK" while 
Finding 1 states "Dublin, Ireland." Please clarify...

Options:
  1. Proceed anyway (ignore conflict)
  2. Stop and review manually
  3. Add clarification note

Your decision (1/2/3):
```

### 4. Report Generation
The **Writer Node** synthesizes validated research into:
- Executive Summary
- Key Financial & Operational Insights
- SWOT Analysis (formatted table)
- 3 Sales Conversation Starters

---
## Roadmap

- [ ] Streamlit Web UI
- [ ] FastAPI REST backend
- [ ] PostgreSQL for research history
- [ ] Multi-company batch processing
- [ ] PDF export functionality
- [ ] Custom search provider integration
- [ ] Supervisor node for multi-agent orchestration

---
## Acknowledgments

- **LangGraph** - State machine orchestration
- **Google Gemini** - AI analysis and generation
- **Tavily** - Web search API
- **LangChain** - LLM framework
