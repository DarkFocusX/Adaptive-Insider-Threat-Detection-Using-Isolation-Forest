import os

import joblib
import numpy as np
from flask import current_app

_model = None
_model_error = None


def load_model():
    """Load Isolation Forest model once (singleton)."""
    global _model, _model_error
    if _model is not None:
        return _model

    model_path = current_app.config.get("MODEL_PATH")
    if not model_path or not os.path.exists(model_path):
        _model_error = f"trained_model.pkl not found at {model_path}"
        current_app.logger.warning(
            "trained_model.pkl not found at %s; using fallback heuristic predictor.",
            model_path,
        )
        _model = None
        return None

    try:
        _model = joblib.load(model_path)
    except Exception as exc:
        _model_error = f"Could not load trained_model.pkl: {exc}"
        current_app.logger.exception("Could not load trained_model.pkl from %s", model_path)
        _model = None
        return None

    _model_error = None
    current_app.logger.info("Isolation Forest model loaded from %s", model_path)
    return _model


def model_status():
    """Return model integration status for admin diagnostics."""
    model_path = current_app.config.get("MODEL_PATH")
    return {
        "path": model_path,
        "exists": bool(model_path and os.path.exists(model_path)),
        "loaded": _model is not None,
        "error": _model_error,
    }


class Predictor:
    """
    Predict Normal vs Anomaly using pre-trained Isolation Forest.

    sklearn IsolationForest:
      predict() ->  1 = inlier (normal), -1 = outlier (anomaly)
      decision_function() -> higher = more normal
    """

    @staticmethod
    def predict(feature_vector):
        feature_vector = np.asarray(feature_vector, dtype=float)
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        if feature_vector.shape[1] != 8:
            raise ValueError(
                "Isolation Forest feature vector must contain 8 values: "
                "login_hour, session_duration, transaction_count, amount_transferred, "
                "download_count, ip_change, new_payee_added, failed_attempts."
            )

        model = load_model()

        if model is None:
            values = feature_vector[0]
            heuristic_score = (
                (values[3] > 100000) * 2
                + (values[6] == 1) * 1
                + (values[4] > 5) * 1
                + (values[7] > 3) * 2
                + (values[5] == 1) * 1
            )
            is_anomaly = heuristic_score >= 2
            return {
                "label": "Anomaly" if is_anomaly else "Normal",
                "is_anomaly": is_anomaly,
                "anomaly_score": float(heuristic_score),
                "model_used": "heuristic_fallback",
            }

        try:
            raw_pred = model.predict(feature_vector)[0]
            decision = float(model.decision_function(feature_vector)[0])
        except Exception as exc:
            current_app.logger.exception("Isolation Forest prediction failed")
            return {
                "label": "Normal",
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "model_used": "prediction_error_fallback",
                "error": str(exc),
            }

        is_anomaly = raw_pred == -1
        return {
            "label": "Anomaly" if is_anomaly else "Normal",
            "is_anomaly": is_anomaly,
            "anomaly_score": decision,
            "model_used": "isolation_forest",
        }
