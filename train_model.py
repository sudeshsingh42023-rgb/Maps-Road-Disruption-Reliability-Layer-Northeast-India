"""Train a closure-report credibility model and report the alerting trade-off.
Run: python train_model.py
"""
import json, joblib, numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, brier_score_loss

df = pd.read_csv("reports_synthetic.csv")
X = pd.get_dummies(df.drop(columns=["report_id", "segment_id", "corridor", "is_true_closure"]),
                   columns=["report_type"])
y = df["is_true_closure"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)

model = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.08, random_state=7)
model.fit(Xtr, ytr)
proba = model.predict_proba(Xte)[:, 1]

# Baseline: naive rule = alert if confirmations > denials
base = (Xte["n_confirmations"] > Xte["n_denials"]).astype(int)
rows = []
for t in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    pred = (proba >= t).astype(int)
    rows.append({"threshold": t, "precision": round(precision_score(yte, pred, zero_division=0), 3),
                 "recall": round(recall_score(yte, pred), 3),
                 "false_alert_rate": round(float(((pred == 1) & (yte == 0)).sum() / max(pred.sum(), 1)), 3)})
metrics = {
    "auc_model": round(roc_auc_score(yte, proba), 3),
    "auc_baseline_rule": round(roc_auc_score(yte, base), 3),
    "brier": round(brier_score_loss(yte, proba), 3),
    "threshold_table": rows, "data": "SYNTHETIC",
}
json.dump(metrics, open("metrics.json", "w"), indent=2)
joblib.dump({"model": model, "columns": list(X.columns)}, "model.joblib")
print(json.dumps(metrics, indent=2))
