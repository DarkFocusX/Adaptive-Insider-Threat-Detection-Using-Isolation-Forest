from flask import session

from models.account import Account
from models.behavior_log import BehaviorLog
from models.user import User
from security_ai.adaptive_response import AdaptiveResponse
from security_ai.alerts import AlertService
from security_ai.behavior_logger import BehaviorLogger
from security_ai.decision_engine import DecisionEngine
from security_ai.feature_extractor import FeatureExtractor
from security_ai.predict import Predictor
from security_ai.trust_score import TrustScore


def run_security_pipeline(
    action_type,
    amount=0.0,
    receiver_account=None,
    is_download=False,
    failed_attempt=0,
    user_id=None,
):
    """
    End-to-end Security AI pipeline:
      log behavior -> extract features -> predict -> trust score ->
      decision -> adaptive response -> alert -> persist
    """
    user_id = user_id or session.get("user_id")
    if not user_id:
        return None

    user = User.get_by_id(user_id)
    if not user or user.get("role") == "admin":
        return None

    behavior = BehaviorLogger.collect(
        action_type=action_type,
        amount=amount,
        receiver_account=receiver_account,
        is_download=is_download,
        failed_attempt=failed_attempt,
        user_id=user_id,
    )

    feature_vector = FeatureExtractor.to_vector(behavior)
    prediction = Predictor.predict(feature_vector)

    is_authenticated = session.get("user_id") == user_id
    if is_authenticated:
        current_trust = float(session.get("trust_score", user.get("trust_score", 95)))
    else:
        current_trust = float(user.get("trust_score", 95))

    new_trust, risk_level = TrustScore.calculate(current_trust, prediction, behavior)
    decision = DecisionEngine.evaluate(new_trust)

    Account.update_trust_score(user_id, new_trust, risk_level)

    BehaviorLog.create(
        user_id=user_id,
        action_type=action_type,
        features=behavior,
        prediction=prediction["label"],
        trust_score=new_trust,
        ip_address=behavior.get("ip_address"),
        risk_level=risk_level,
        decision=decision.get("access_level"),
        model_used=prediction.get("model_used"),
        anomaly_score=prediction.get("anomaly_score"),
    )

    if is_authenticated:
        AdaptiveResponse.apply(new_trust, risk_level, decision)

    AlertService.maybe_create(
        user_id=user_id,
        trust_score=new_trust,
        risk_level=risk_level,
        prediction_label=prediction["label"],
        behavior=behavior,
        decision=decision,
    )

    if is_authenticated:
        session["last_prediction"] = prediction["label"]

    return {
        "behavior": behavior,
        "features": FeatureExtractor.explain(behavior),
        "prediction": prediction,
        "trust_score": new_trust,
        "risk_level": risk_level,
        "decision": decision,
    }
