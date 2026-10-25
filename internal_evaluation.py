"""
internal_evaluation.py
----------------------------------------------------------------------------
Produces the INTERNAL model results promised in Chapter 3 (Data Analysis):
  - confusion matrix of the deployed XGBoost model on the 20% holdout set
  - precision, recall, F1 per class
  - overall accuracy, weighted F1, and macro F1
  - the same results for the actual JRS-WQMA records only (synthetic excluded)
  - the class distribution at each stage (Table 6 check)

HOW TO RUN (same folder as wqi_pipeline.py, after the pipeline has been run):
    python internal_evaluation.py
Optional: point to the model files that the website actually uses, e.g.
    python internal_evaluation.py --model-dir backend/models

It does NOT retrain anything. It rebuilds the exact same dataset and
train/test split as wqi_pipeline.py (same random_state = 42) and evaluates
the saved model on the holdout records.
Outputs are printed and saved in outputs/internal_evaluation/.
----------------------------------------------------------------------------
"""
import os, sys, io, argparse, contextlib
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (confusion_matrix, classification_report, accuracy_score,
                             f1_score, precision_recall_fscore_support)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wqi_pipeline as wp   # the developer's pipeline (main() is not executed on import)

ap = argparse.ArgumentParser()
ap.add_argument('--model-dir', default=wp.MODEL_DIR, help='folder with xgboost_model.pkl, scaler.pkl, label_encoder.pkl')
ap.add_argument('--model-file', default='xgboost_model.pkl')
args = ap.parse_args()

OUT = os.path.join(wp.OUTPUT_DIR, 'internal_evaluation')
os.makedirs(OUT, exist_ok=True)

# ---- 1. Rebuild the dataset exactly as the pipeline does (quietly) ----
with contextlib.redirect_stdout(io.StringIO()):
    df = wp.load_data(wp.INPUT_CSV)
    df = wp.preprocess_data(df)
    n_real = len(df)
    df = wp.seed_clean_data(df)
    df = wp.compute_wqi_column(df)
    df = wp.create_classification_target(df)
df['Is_Synthetic'] = np.arange(len(df)) >= n_real

# ---- 2. Load the saved (deployed) model, scaler and label encoder ----
model = joblib.load(os.path.join(args.model_dir, args.model_file))
scaler = joblib.load(os.path.join(args.model_dir, 'scaler.pkl'))
le = joblib.load(os.path.join(args.model_dir, 'label_encoder.pkl'))
X_scaled = scaler.transform(df[wp.TRAINING_FEATURES])
y = le.transform(df['WQI_Class'])
idx = np.arange(len(df))

# Same split call as wqi_pipeline.py (adding idx does not change the split)
X_tr, X_te, y_tr, y_te, i_tr, i_te = train_test_split(
    X_scaled, y, idx, test_size=0.2, random_state=42, stratify=y)

order = [c for c in ['Excellent', 'Good', 'Fair', 'Poor', 'High Risk'] if c in le.classes_]
labels = le.transform(order)

def evaluate(mask, title, tag):
    yt, yp = y_te[mask], model.predict(X_te[mask])
    yp = np.asarray(yp).astype(int).ravel()
    cm = confusion_matrix(yt, yp, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f'Actual {c}' for c in order], columns=[f'Pred {c}' for c in order])
    p, r, f, s = precision_recall_fscore_support(yt, yp, labels=labels, zero_division=0)
    per = pd.DataFrame({'Class': order, 'Precision': p, 'Recall': r, 'F1': f, 'Support': s})
    present = [l for l in labels if (yt == l).any()]   # classes that occur in this subset
    summ = pd.DataFrame({'Metric': ['Records', 'Classes present', 'Accuracy', 'Weighted F1', 'Macro F1 (classes present)'],
                         'Value': [len(yt), len(present), accuracy_score(yt, yp),
                                   f1_score(yt, yp, labels=present, average='weighted', zero_division=0),
                                   f1_score(yt, yp, labels=present, average='macro', zero_division=0)]})
    print('\n' + '=' * 70 + f'\n{title}\n' + '=' * 70)
    print(summ.round(4).to_string(index=False))
    print('\nConfusion matrix (rows = actual WAWQI class, columns = predicted):')
    print(cm_df.to_string())
    print('\nPer-class results (support = number of holdout records in the class):')
    print(per.round(4).to_string(index=False))
    print('Note: classes with Support = 0 have no records in this subset; their scores are not meaningful.')
    cm_df.to_csv(os.path.join(OUT, f'confusion_matrix_{tag}.csv'))
    per.to_csv(os.path.join(OUT, f'per_class_{tag}.csv'), index=False)
    summ.to_csv(os.path.join(OUT, f'summary_{tag}.csv'), index=False)

print('Model file :', os.path.join(args.model_dir, args.model_file))
print('Model type :', type(model).__name__)
try:
    print('Parameters :', {k: v for k, v in model.get_params().items()
                           if k in ('n_estimators', 'max_depth', 'learning_rate')})
except Exception:
    pass

syn_te = df['Is_Synthetic'].values[i_te]
evaluate(np.ones(len(i_te), bool), 'A. FULL HOLDOUT SET (actual + synthetic records)', 'full')
evaluate(~syn_te, 'B. ACTUAL JRS-WQMA RECORDS ONLY (synthetic excluded)', 'actual_only')

# ---- 3. Class distribution at each stage (check against Chapter 3, Table 6) ----
cls = df['WQI_Class']
dist = pd.DataFrame({
    'Historical': cls[~df['Is_Synthetic']].value_counts(),
    'Synthetic': cls[df['Is_Synthetic']].value_counts(),
    'Combined': cls.value_counts(),
    'Training': pd.Series(le.inverse_transform(y_tr)).value_counts(),
    'Holdout': pd.Series(le.inverse_transform(y_te)).value_counts(),
}).reindex(order).fillna(0).astype(int)
dist.loc['Total'] = dist.sum()
print('\n' + '=' * 70 + '\nC. CLASS DISTRIBUTION (compare with Chapter 3, Table 6)\n' + '=' * 70)
print(dist.to_string())
dist.to_csv(os.path.join(OUT, 'class_distribution.csv'))
print(f'\nAll tables saved in: {OUT}')
print('Please send the whole printed output (or the CSV files in that folder).')
