from imapclient import IMAPClient
import pyzmail
import re
import nltk
import pandas as pd

from fpdf import FPDF
from datetime import datetime, timedelta
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# =========================
# AI SETUP
# =========================
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

def clean_for_pdf(text):
    # Hilangkan emoji / unicode agar PDF tidak error
    return text.encode("latin-1", "ignore").decode("latin-1")

# Load dataset
data = pd.read_csv("data/phishing_email.csv")
data["clean_text"] = data["text"].apply(clean_text)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data["clean_text"])
y = data["label"]

model = MultinomialNB()
model.fit(X, y)

# =========================
# PDF SETUP
# =========================
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "AI Phishing Detection Report", ln=True)

pdf.set_font("Arial", "", 10)
pdf.cell(0, 8, f"Tanggal Scan: {datetime.now()}", ln=True)
pdf.ln(5)

# ===== TABLE HEADER =====
pdf.set_font("Arial", "B", 10)
pdf.cell(10, 8, "No", border=1)
pdf.cell(90, 8, "Subject", border=1)
pdf.cell(35, 8, "Status", border=1)
pdf.cell(25, 8, "Confidence", border=1)
pdf.ln()

# =========================
# EMAIL CONFIG
# =========================
EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"  # APP PASSWORD (tanpa spasi)

# =========================
# BACA EMAIL (1 HARI TERAKHIR)
# =========================
with IMAPClient("imap.gmail.com") as server:
    server.login(EMAIL, PASSWORD)
    server.select_folder("INBOX", readonly=True)

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    messages = server.search(["SINCE", yesterday, "UNSEEN"])[-10:]

    print("Email diproses:", len(messages))

    index = 1
    for uid in messages:
        raw = server.fetch(uid, ["BODY[]"])
        message = pyzmail.PyzMessage.factory(raw[uid][b"BODY[]"])

        subject = message.get_subject()
        body = ""

        if message.text_part:
            payload = message.text_part.get_payload()
            charset = message.text_part.charset
            body = payload.decode(charset or "utf-8", errors="ignore")

        clean_body = clean_text(body)
        vector = vectorizer.transform([clean_body])

        prediction = model.predict(vector)[0]
        probability = model.predict_proba(vector)[0]
        conf = round(max(probability) * 100, 2)

        if conf < 60:
            status = "UNKNOWN"
        elif prediction == 1:
            status = "PHISHING"
        else:
            status = "AMAN"

        # ===== PDF ROW =====
        pdf.set_font("Arial", "", 10)
        pdf.cell(10, 8, str(index), border=1)
        pdf.cell(90, 8, clean_for_pdf(subject)[:60], border=1)
        pdf.cell(35, 8, status, border=1)
        pdf.cell(25, 8, f"{conf}%", border=1)
        pdf.ln()

        # ===== TERMINAL OUTPUT =====
        print("\nSUBJECT:", subject)
        print("STATUS :", status)
        print("CONFIDENCE:", conf, "%")

        index += 1

# =========================
# SIMPAN PDF
# =========================
filename = f"phishing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
pdf.output(filename)

print(f"\n📄 Report berhasil dibuat: {filename}")
