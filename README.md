# 🔧 NCR AI Assistant (5W1H Intelligence System)

## 📌 Project Overview
The **NCR AI Assistant** is an AI-powered Streamlit application designed to improve the quality of Non-Conformance Report (NCR) descriptions in wind turbine inspection reports.

It uses **Google Gemini LLM** to extract structured **5W1H (What, Where, When, Why, Who, How)** information from unstructured maintenance text and evaluates report completeness using scoring algorithms.

---

## 🎯 Problem Statement
Industrial NCR reports are often:
- Unstructured
- Incomplete
- Ambiguous
- Hard to analyze for root cause detection

This system transforms free-text NCR descriptions into:
✔ Structured information  
✔ Quality-scored reports  
✔ Improved standardized descriptions  

---

## 🧠 Key Features

- 🔍 5W1H Extraction using Gemini AI
- 📊 Completeness Scoring (0–6)
- 📈 Semantic Quality Scoring (0–4)
- 🧾 Automatic NCR Improvement Suggestion
- 📂 Dataset-based testing + Manual input mode
- ⚠️ Missing field detection
- 💬 Feedback logging system

---

## 🏗️ System Architecture

User Input (NCR Text)
↓
Streamlit UI (app_main.py)
↓
NCR Analyzer (Gemini LLM)
↓
5W1H Extraction + Cleaning
↓
Scoring Engine (Completeness + Semantic)
↓
Final Output Dashboard

---

## 📁 Project Structure

```bash
ncr-ai-assistant/
│
├── app_main.py          # Streamlit UI
├── config.py            # Gemini model configuration
├── ncr_analyzer.py      # AI processing and parsing logic
├── scoring.py           # Evaluation and scoring system
├── requirements.txt     # Project dependencies
├── .gitignore           # Security and ignored files
├── .env                 # API key and environment variables (local only)
└── dataset.xlsx         # NCR dataset
```

---

## ⚙️ Tech Stack

- Python 🐍
- Streamlit 📊
- Google Gemini AI 🤖
- Pandas 📁
- Regular Expressions (Regex)
- dotenv (Environment management)

---

## 🚀 How to Run the Project

```bash
1️⃣ Clone the repository

git clone https://github.com/your-username/ncr-ai-assistant.git
cd ncr-ai-assistant

2️⃣ Install dependencies

pip install -r requirements.txt

3️⃣ Setup API key

create .env file , paste your api key:
GEMINI_API_KEY=your_api_key_here

Get Key here : https://aistudio.google.com/api-keys 

1. Create New Project.
2. Using this project , Create new API key in API keys.
3. Use the key in .env file.

4️⃣ Run the app

In terminal , run this command

streamlit run app_main.py
