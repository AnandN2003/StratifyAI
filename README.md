# StratifyAI - Autonomous Company Research Agent

[![Python](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-brightgreen.svg)](https://www.docker.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-orchestration-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-purple.svg)](https://ai.google.dev/)

> **An intelligent AI agent that autonomously researches companies, detects conflicting information, and generates professional account plans for sales due diligence.**

---

## 📖 Overview

StratifyAI is an **Agentic AI system** built with LangGraph that combines web search, LLM-powered analysis, and human-in-the-loop decision making to create comprehensive company research reports. Perfect for sales teams, investors, and business analysts who need fast, reliable company intelligence.

### ✨ Key Features

- 🔍 **Autonomous Web Research** - Searches 12+ sources per company using Tavily API
- 🤖 **AI-Powered Conflict Detection** - Gemini 2.5 Flash identifies factual discrepancies
- 👤 **Human-in-the-Loop** - Interactive prompts for critical decisions when conflicts arise
- 📊 **Structured Account Plans** - Professional reports with SWOT analysis and sales insights
- 🐳 **Fully Dockerized** - Reproducible environment, runs anywhere
- ⚡ **Fast Execution** - Complete research and report in 30-45 seconds

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

📘 **[View Full Workflow Documentation →](./WORKFLOW.md)**

---

## Quick Start

### Prerequisites

- Docker Desktop installed
- API Keys:
  - **Google Gemini API** (free tier: 1,500 requests/day)
  - **Tavily Search API** (free tier: 1,000 searches/month)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AnandN2003/StratifyAI.git
cd StratifyAI
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Get API Keys**
- **Gemini:** https://makersuite.google.com/app/apikey
- **Tavily:** https://tavily.com/

4. **Build the Docker container**
```bash
docker-compose build
```

5. **Run the agent**
```bash
docker-compose run --rm stratify-ai
```

### Usage

```bash
Enter company name to research: Microsoft

# Agent will:
# 1. Search 12 web sources
# 2. Analyze for conflicts
# 3. Prompt you if issues found
# 4. Generate professional report
```

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

## 🎯 Use Cases

- **Sales Teams** - Pre-call research and account planning
- **Investment Analysts** - Company due diligence
- **Business Development** - Partner evaluation
- **Consultants** - Client background research
- **Market Research** - Competitive intelligence

---

## 📁 Project Structure

```
StratifyAI/
├── src/
│   ├── graph.py           # LangGraph nodes, prompts, workflow
│   ├── entrypoint.py      # CLI interface
│   └── __init__.py
├── app/
│   └── streamlit_app.py   # Future UI (placeholder)
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # Python 3.9 environment
├── requirements.txt       # Dependencies
├── .env.example           # API key template
├── WORKFLOW.md            # Detailed documentation
└── README.md              # This file
```

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
## 🚧 Roadmap

- [ ] Streamlit Web UI
- [ ] FastAPI REST backend
- [ ] PostgreSQL for research history
- [ ] Multi-company batch processing
- [ ] PDF export functionality
- [ ] Custom search provider integration
- [ ] Supervisor node for multi-agent orchestration

---
## 🙏 Acknowledgments

- **LangGraph** - State machine orchestration
- **Google Gemini** - AI analysis and generation
- **Tavily** - Web search API
- **LangChain** - LLM framework