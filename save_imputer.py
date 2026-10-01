import pandas as pd
import joblib
from sklearn.impute import KNNImputer
import os

FEATURE_COLS = ["DO", "BOD", "TSS", "pH", "Temperature", "Fecal_Coliform"]
df = pd.read_csv("datasets/WQMA_JRS_2020_2025.csv")

imputer = KNNImputer(n_neighbors=5, metric="nan_euclidean")
imputer.fit(df[FEATURE_COLS])

os.makedirs(os.path.join("backend", "models"), exist_ok=True)
joblib.dump(imputer, os.path.join("backend", "models", "imputer.pkl"))

print("Imputer saved successfully!")
