import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
df = pd.read_csv("datasets/sql_logs/sample_sql_logs.csv")

print("=" * 80)
print("ORIGINAL DATASET")
print(df)
print("=" * 80)

# TF-IDF vectorization
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["query_text"])

print("TF-IDF MATRIX SHAPE:")
print(X.shape)

print("=" * 80)

feature_names = vectorizer.get_feature_names_out()

print("FEATURE NAMES:")
print(feature_names)

print("=" * 80)

print("TF-IDF MATRIX:")
print(X.toarray())
