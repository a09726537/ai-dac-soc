import pandas as pd
import numpy as np
import shap

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest


df = pd.read_csv(
    "datasets/sql_logs/sample_sql_logs.csv"
)

queries = df["query_text"]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(queries)

X_dense = X.toarray()

model = IsolationForest(
    contamination=0.2,
    random_state=42
)

model.fit(X_dense)

explainer = shap.Explainer(
    model.predict,
    X_dense
)

shap_values = explainer(X_dense)

print("=" * 80)
print("SHAP EXPLAINABILITY")
print("=" * 80)

feature_names = vectorizer.get_feature_names_out()

for i in range(len(queries)):

    print("\nQUERY:")
    print(queries.iloc[i])

    values = shap_values.values[i]

    top_indices = np.argsort(np.abs(values))[-5:]

    print("\nTOP TOKENS:")

    for idx in reversed(top_indices):

        print(
            f"{feature_names[idx]} -> "
            f"{round(values[idx], 5)}"
        )

    print("-" * 80)
