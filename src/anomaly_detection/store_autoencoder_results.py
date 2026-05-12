import pandas as pd
import numpy as np
import psycopg2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.losses import MeanSquaredError


# -------------------------------------------------------------------
# LOAD DATASET
# -------------------------------------------------------------------

df = pd.read_csv("datasets/sql_logs/sample_sql_logs.csv")

print("=" * 80)
print("DATASET LOADED")
print(df)
print("=" * 80)


# -------------------------------------------------------------------
# TF-IDF VECTORIZATION
# -------------------------------------------------------------------

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df["query_text"])

X = X.toarray()

print("TF-IDF MATRIX SHAPE:", X.shape)


# -------------------------------------------------------------------
# NORMALIZATION
# -------------------------------------------------------------------

scaler = MinMaxScaler()

X_scaled = scaler.fit_transform(X)

input_dim = X_scaled.shape[1]

print("INPUT DIMENSION:", input_dim)


# -------------------------------------------------------------------
# AUTOENCODER MODEL
# -------------------------------------------------------------------

input_layer = Input(shape=(input_dim,))

encoded = Dense(16, activation="relu")(input_layer)
encoded = Dense(8, activation="relu")(encoded)

decoded = Dense(16, activation="relu")(encoded)
decoded = Dense(input_dim, activation="sigmoid")(decoded)

autoencoder = Model(
    inputs=input_layer,
    outputs=decoded
)

autoencoder.compile(
    optimizer="adam",
    loss=MeanSquaredError()
)

print("=" * 80)
print("TRAINING AUTOENCODER...")
print("=" * 80)


# -------------------------------------------------------------------
# TRAINING
# -------------------------------------------------------------------

autoencoder.fit(
    X_scaled,
    X_scaled,
    epochs=50,
    batch_size=2,
    shuffle=True,
    verbose=0
)

print("TRAINING COMPLETED")


# -------------------------------------------------------------------
# RECONSTRUCTION
# -------------------------------------------------------------------

reconstructed = autoencoder.predict(
    X_scaled,
    verbose=0
)

mse = np.mean(
    np.power(X_scaled - reconstructed, 2),
    axis=1
)

df["reconstruction_error"] = mse


# -------------------------------------------------------------------
# THRESHOLD
# -------------------------------------------------------------------

threshold = np.mean(mse) + np.std(mse)

df["ml_anomaly"] = df["reconstruction_error"] > threshold

print("=" * 80)
print("ANOMALY DETECTION RESULTS")
print("=" * 80)

print(df[[
    "query_text",
    "reconstruction_error",
    "ml_anomaly"
]])

print("=" * 80)
print("THRESHOLD:", threshold)
print("=" * 80)


# -------------------------------------------------------------------
# POSTGRESQL CONNECTION
# -------------------------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="aidac",
    user="william",
    password="Oracle2020"
)

cur = conn.cursor()


# -------------------------------------------------------------------
# CREATE TABLE
# -------------------------------------------------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS ml_anomaly_results (

    id SERIAL PRIMARY KEY,

    username TEXT,

    database_name TEXT,

    query_text TEXT,

    reconstruction_error NUMERIC,

    threshold NUMERIC,

    ml_anomaly BOOLEAN,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")


# -------------------------------------------------------------------
# INSERT RESULTS
# -------------------------------------------------------------------

for _, row in df.iterrows():

    cur.execute("""
        INSERT INTO ml_anomaly_results (

            username,
            database_name,
            query_text,
            reconstruction_error,
            threshold,
            ml_anomaly

        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (

        row["username"],
        row["database_name"],
        row["query_text"],
        float(row["reconstruction_error"]),
        float(threshold),
        bool(row["ml_anomaly"])

    ))


conn.commit()

print("=" * 80)
print("RESULTS INSERTED INTO POSTGRESQL")
print("=" * 80)


# -------------------------------------------------------------------
# VERIFY INSERTION
# -------------------------------------------------------------------

cur.execute("""
SELECT
    id,
    username,
    query_text,
    reconstruction_error,
    threshold,
    ml_anomaly
FROM ml_anomaly_results
ORDER BY id DESC
LIMIT 10;
""")

rows = cur.fetchall()

for row in rows:

    print(row)

print("=" * 80)


# -------------------------------------------------------------------
# CLEANUP
# -------------------------------------------------------------------

cur.close()

conn.close()

print("POSTGRESQL CONNECTION CLOSED")
