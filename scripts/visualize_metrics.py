#!/usr/bin/env python3
"""
Visualize evaluation metrics:
 - Baseline RMSE
 - Model RMSE
 - Direction Accuracy
"""
import os
import json
import matplotlib.pyplot as plt
def main():
    metrics_path = os.path.join('reports', 'metrics', 'evaluation_metrics.json')
    if not os.path.isfile(metrics_path):
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    labels = ['Baseline RMSE', 'Model RMSE', 'Direction Accuracy']
    values = [
        metrics.get('baseline_rmse', 0),
        metrics.get('model_rmse', 0),
        metrics.get('direction_accuracy', 0)
    ]

    plt.figure()
    plt.bar(labels, values)
    plt.title('Evaluation Metrics')
    plt.ylabel('Value')
    plt.tight_layout()

    out_dir = os.path.join('results', 'plots')
    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, 'evaluation_metrics.png')
    plt.savefig(save_path)
    plt.close()

    print(f"Evaluation metrics plot saved to {save_path}")
