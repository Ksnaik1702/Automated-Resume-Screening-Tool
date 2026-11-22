"""
Model Evaluation and Sanity Checks Module
Computes ranking metrics, ROC-AUC, PR-AUC, and Top-K precision on benchmark pairs.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


def evaluate_ranking_performance(csv_path: str | Path, threshold: float = 0.65) -> Dict[str, Any]:
    """
    Evaluates scoring quality on labeled (candidate_name, score, label) pairs.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"Evaluation benchmark file not found at {csv_path}")
        
    df = pd.read_csv(p)
    if "score" not in df.columns or "label" not in df.columns:
        raise ValueError("Benchmark CSV must contain 'score' and 'label' columns.")
        
    y_true = df["label"].values
    y_scores = df["score"].values
    y_pred = (y_scores >= threshold).astype(int)
    
    # Ranking metrics
    try:
        roc_auc = float(roc_auc_score(y_true, y_scores))
    except Exception:
        roc_auc = 0.0
        
    try:
        pr_auc = float(average_precision_score(y_true, y_scores))
    except Exception:
        pr_auc = 0.0
        
    # Top-K Precision
    sorted_df = df.sort_values(by="score", ascending=False)
    top_3_precision = float(sorted_df.head(3)["label"].mean())
    top_5_precision = float(sorted_df.head(5)["label"].mean())
    
    # Classification metrics at threshold
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    metrics = {
        "ROC_AUC": round(roc_auc, 4),
        "PR_AUC": round(pr_auc, 4),
        "Top_3_Precision": round(top_3_precision, 4),
        "Top_5_Precision": round(top_5_precision, 4),
        "Precision_at_threshold": round(prec, 4),
        "Recall_at_threshold": round(rec, 4),
        "F1_Score": round(f1, 4),
        "Confusion_Matrix": {
            "True_Positives": int(tp),
            "False_Positives": int(fp),
            "True_Negatives": int(tn),
            "False_Negatives": int(fn)
        }
    }
    
    return metrics


def print_evaluation_report(metrics: Dict[str, Any]):
    """Pretty prints the evaluation benchmark report."""
    print("\n" + "=" * 55)
    print("       MODEL EVALUATION & BENCHMARK METRICS       ")
    print("=" * 55)
    print(f"  Area Under ROC Curve (ROC-AUC)   : {metrics['ROC_AUC']:.4f}")
    print(f"  Precision-Recall AUC (PR-AUC)    : {metrics['PR_AUC']:.4f}")
    print(f"  Top-3 Candidate Precision        : {metrics['Top_3_Precision'] * 100:.1f}%")
    print(f"  Top-5 Candidate Precision        : {metrics['Top_5_Precision'] * 100:.1f}%")
    print(f"  Precision (Score >= 0.65)        : {metrics['Precision_at_threshold']:.4f}")
    print(f"  Recall (Score >= 0.65)           : {metrics['Recall_at_threshold']:.4f}")
    print(f"  F1-Score                         : {metrics['F1_Score']:.4f}")
    print("-" * 55)
    cm = metrics["Confusion_Matrix"]
    print(f"  Confusion Matrix: TP={cm['True_Positives']}, FP={cm['False_Positives']}, TN={cm['True_Negatives']}, FN={cm['False_Negatives']}")
    print("=" * 55 + "\n")
