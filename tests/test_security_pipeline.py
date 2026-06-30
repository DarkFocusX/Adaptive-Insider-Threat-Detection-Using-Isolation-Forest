import pytest

from security_ai.decision_engine import DecisionEngine
from security_ai.feature_extractor import FeatureExtractor
from security_ai.predict import Predictor
from security_ai.trust_score import TrustScore


def test_trust_risk_bands():
    assert TrustScore.get_risk_level(95) == "Safe"
    assert TrustScore.get_risk_level(80) == "Low Risk"
    assert TrustScore.get_risk_level(55) == "Medium Risk"
    assert TrustScore.get_risk_level(25) == "High Risk"


def test_decision_engine_full_access():
    decision = DecisionEngine.evaluate(95)
    assert decision["access_level"] == "full"
    assert decision["disable_transfer"] is False


def test_decision_engine_restrict():
    decision = DecisionEngine.evaluate(30)
    assert decision["access_level"] == "restrict"
    assert decision["disable_transfer"] is True
    assert decision["disable_withdraw"] is True
    assert decision["generate_alert"] is True


def test_anomaly_reduces_trust():
    current = 95
    prediction = {"is_anomaly": True}
    behavior = {
        "action_type": "transfer",
        "amount_transferred": 60000,
        "ip_change": 1,
    }
    new_score, _risk = TrustScore.calculate(current, prediction, behavior)
    assert new_score < current


def test_predictor_accepts_eight_feature_vector(app):
    behavior = {
        "login_hour": 10,
        "session_duration": 30,
        "transaction_count": 2,
        "amount_transferred": 5000,
        "download_count": 1,
        "ip_change": 0,
        "new_payee_added": 0,
        "failed_attempts": 0,
    }
    with app.app_context():
        result = Predictor.predict(FeatureExtractor.to_vector(behavior))
    assert result["label"] in {"Normal", "Anomaly"}
    assert result["model_used"] in {
        "heuristic_fallback",
        "isolation_forest",
        "prediction_error_fallback",
    }
