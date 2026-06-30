from models.alert import Alert


class AlertService:
    """Create security alerts when risk thresholds are crossed."""

    @staticmethod
    def maybe_create(user_id, trust_score, risk_level, prediction_label, behavior, decision):
        if not decision.get("generate_alert"):
            return None

        severity = "High" if trust_score < 40 else "Medium"
        message = (
            f"{prediction_label} behavior during {behavior.get('action_type')} "
            f"(trust={trust_score}, risk={risk_level}). "
            f"Features: amount={behavior.get('amount_transferred')}, "
            f"ip_change={behavior.get('ip_change')}, "
            f"new_payee={behavior.get('new_payee_added')}."
        )

        return Alert.create(
            user_id=user_id,
            alert_type="Insider Threat",
            severity=severity,
            message=message,
        )
