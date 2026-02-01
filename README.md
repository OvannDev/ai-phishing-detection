# AI Phishing Detection System

This project is a **Python-based AI system** for detecting phishing emails using
**Machine Learning (NLP)** and **real email ingestion via IMAP**.

##  Features
- Phishing detection using **Naive Bayes + TF-IDF**
- Reads real emails securely via **IMAP (App Password)**
- Time-based scanning (last 24 hours)
- Confidence threshold with **UNKNOWN** state
- PDF report generation (table format)

##  How It Works
1. Emails are fetched from inbox (IMAP)
2. Email body is cleaned and vectorized
3. ML model classifies email as:
   - PHISHING
   - AMAN
   - UNKNOWN
4. Results are exported into a **PDF security report**

##  Tech Stack
- Python
- scikit-learn
- NLTK
- IMAPClient
- FPDF

##  Security & Ethics
- Uses **read-only IMAP**
- Requires **App Password**, not real email password
- Intended for **personal or educational use only**

##  How to Run
```bash
pip install -r requirements.txt
python email_reader.py

