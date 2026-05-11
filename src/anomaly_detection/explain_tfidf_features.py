import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("datasets/sql_logs/sample_sql_logs.csv")

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["query_text"]).toarray()
features = vectorizer.get_feature_names_out()

for i, query in enumerate(df["query_text"]):
    print("=" * 80)
    print("QUERY:", query)

    feature_scores = list(zip(features, X[i]))
    feature_scores = sorted(feature_scores, key=lambda x: x[1], reverse=True)

    print("TOP EXPLANATORY FEATURES:")
    for feature, score in feature_scores[:5]:
        if score > 0:
            print(f"- {feature}: {score:.4f}")
