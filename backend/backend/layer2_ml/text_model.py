from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os


def train_model(texts, labels):

    # 🔥 Improved vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        stop_words="english"
    )

    X = vectorizer.fit_transform(texts)

    # 🔥 Improved model
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000
    )

    model.fit(X, labels)

    # Create models folder
    os.makedirs("models", exist_ok=True)

    # Save models
    with open("models/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    with open("models/text_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("✅ Model trained and saved successfully")