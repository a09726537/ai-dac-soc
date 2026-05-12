import pandas as pd
import numpy as np
import shap
import psycopg2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest


DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "aidac",
    "user": "william",
    "password": "Oracle2020"
}


df = pd.read_csv("datasets/sql_logs/sample_sql_logs.csv")

if df.empty:
    raise ValueError("Dataset is empty.")

if "query_text" not in df.columns:
    raise ValueError("Column 'query_text' not found in dataset.")

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["query_text"]).toarray()

feature_names = vectorizer.get_feature_names_out()

model = IsolationForest(
    contamination=0.2,
    random_state=42
)

model.fit(X)

explainer = shap.Explainer(
    model.predict,
    X
)

shap_values = explainer(X)

conn = psycopg2.connect(**DB_CONFIG)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS shap_explanations (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    top_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("TRUNCATE TABLE shap_explanations RESTART IDENTITY;")

for i, query in enumerate(df["query_text"]):

    values = shap_values.values[i]

    top_indices = np.argsort(np.abs(values))[-5:][::-1]

    features = []

    for idx in top_indices:

        feature_name = feature_names[idx]

        feature_value = round(float(values[idx]), 5)

        features.append(f"{feature_name}={feature_value}")

    cur.execute("""
        INSERT INTO shap_explanations (
            query_text,
            top_features
        )
        VALUES (%s, %s);
    """, (
        query,
        ", ".join(features)
    ))

conn.commit()

cur.execute("""
SELECT
    id,
    query_text,
    top_features
FROM shap_explanations
ORDER BY id;
""")

rows = cur.fetchall()

print("=" * 80)
print("SHAP EXPLANATIONS STORED IN POSTGRESQL")
print("=" * 80)

for row in rows:
    print(row)

print("=" * 80)

cur.close()

conn.close()

print("POSTGRESQL CONNECTION CLOSED")
