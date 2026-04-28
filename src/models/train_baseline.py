import json
import os
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def train_and_evaluate():
    # Load data
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # MLflow Tracking
    mlflow.set_tracking_uri("sqlite:///mlruns.db")
    mlflow.set_experiment("iris_baseline_experiment")
    
    with mlflow.start_run(run_name="baseline_logistic_regression"):
        # Model
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=200, C=10, random_state=42))
        clf.fit(X_train, y_train)
        
        # Predictions
        y_pred = clf.predict(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1_scores = f1_score(y_test, y_pred, average=None)
        f1_virginica = float(f1_scores[2])
        
        # Log to MLflow
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score_virginica", f1_virginica)
        mlflow.sklearn.log_model(clf, "model")
        
        # Save model locally for inference
        import joblib
        os.makedirs("models", exist_ok=True)
        joblib.dump(clf, "models/latest_model.pkl")
        
        # Save metrics
        os.makedirs("reports", exist_ok=True)
        metrics_dict = {
            "accuracy": accuracy,
            "f1_score_virginica": f1_virginica
        }
        with open("reports/metrics.json", "w") as f:
            json.dump(metrics_dict, f, indent=4)
        
        print(f"Model trained. Accuracy: {accuracy:.4f}, F1 Virginica: {f1_virginica:.4f}")

if __name__ == "__main__":
    train_and_evaluate()

