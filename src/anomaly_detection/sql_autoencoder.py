import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.losses import MeanSquaredError

# -------------------------------------------------------------------
# LOAD DATASET
# -------------------------------------------------------------------

df = pd.read_csv("datasets/sql_logs/sample_sql_logs.csv")

queries = df["query_text"]

# -------------------------------------------------------------------
# TF-IDF VECTORIZATION
# -------------------------------------------------------------------

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(queries)

X = X.toarray()

# -------------------------------------------------------------------
# NORMALIZATION
# -------------------------------------------------------------------

scaler = MinMaxScaler()

X_scaled = scaler.fit_transform(X)

input_dim = X_scaled.shape[1]

# -------------------------------------------------------------------
# AUTOENCODER ARCHITECTURE
# -------------------------------------------------------------------

input_layer = Input(shape=(input_dim,))

encoded = Dense(16, activation='relu')(input_layer)
encoded = Dense(8, activation='relu')(encoded)

decoded = Dense(16, activation='relu')(encoded)
decoded = Dense(input_dim, activation='sigmoid')(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

autoencoder.compile(
    optimizer='adam',
    loss=MeanSquaredError()
)

# -------------------------------------------------------------------
# TRAINING
# -------------------------------------------------------------------

autoencoder.fit(
    X_scaled,
    X_scaled,
    epochs=50,
    batch_size=2,
    shuffle=True,
    verbose=1
)

# -------------------------------------------------------------------
# RECONSTRUCTION ERROR
# -------------------------------------------------------------------

reconstructed = autoencoder.predict(X_scaled)

mse = np.mean(np.power(X_scaled - reconstructed, 2), axis=1)

df["reconstruction_error"] = mse

# -------------------------------------------------------------------
# THRESHOLD
# -------------------------------------------------------------------

threshold = np.mean(mse) + np.std(mse)

df["anomaly"] = df["reconstruction_error"] > threshold

# -------------------------------------------------------------------
# RESULTS
# -------------------------------------------------------------------

print("=" * 80)

print(df[[
    "query_text",
    "reconstruction_error",
    "anomaly"
]])

print("=" * 80)

print(f"THRESHOLD: {threshold}")

