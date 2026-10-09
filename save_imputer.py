"""
save_imputer.py
Sometimes when we collect water samples, a sensor might fail or not all features are measured, leaving us with missing data 
(like a missing pH reading, no BOD, etc). This script trains a smart tool (called an "imputer") 
to guess those missing numbers by looking at past water samples that are very similar.
We then save this tool so our website can use it later.
"""

import pandas as pd
import joblib
from sklearn.impute import KNNImputer
import os

# 1. These are the 6 chemical tests (features) we care about.
FEATURE_COLS = ["DO", "BOD", "TSS", "pH", "Temperature", "Fecal_Coliform"]

# 2. Open our historical record of water tests.
df = pd.read_csv("datasets/WQMA_JRS_2020_2025.csv")

# 3. Create the 'smart guesser' tool. 
# It will look at the 5 most similar water samples to figure out any missing number.
imputer = KNNImputer(n_neighbors=5, metric="nan_euclidean")

# 4. Have the tool study our historical data so it learns the patterns.
imputer.fit(df[FEATURE_COLS])

# 5. Make sure the folder exists where we want to save our tool.
os.makedirs(os.path.join("backend", "models"), exist_ok=True)

# 6. Save the trained tool as a file so our website can load it up instantly.
joblib.dump(imputer, os.path.join("backend", "models", "imputer.pkl"))

print("Imputer saved successfully to backend/models/imputer.pkl!")
