import re
import nltk
import pandas as pd

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# download stopwords
nltk.download('stopwords')

# stopwords
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

# training ulang (demo mode)
data = pd.read_csv("data/phishing_email.csv")
data['clean_text'] = data['text'].apply(clean_text)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['clean_text'])
y = data['label']

model = MultinomialNB()
model.fit(X, y)

# ===============================
# TEST MANUAL
# ===============================
print("\n=== AI PHISHING DETECTION ===")
user_input = input("Masukkan teks email: ")

clean_input = clean_text(user_input)
vector_input = vectorizer.transform([clean_input])

prediction = model.predict(vector_input)[0]
probability = model.predict_proba(vector_input)[0]

label = "PHISHING ❌" if prediction == 1 else "AMAN ✅"

print("\nHasil Deteksi:")
print("Status:", label)
print("Confidence:", round(max(probability) * 100, 2), "%")
