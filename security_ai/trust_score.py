class TrustScore:
    """
    Adaptive trust score (0–100) with risk bands:
      90–100  Safe
      70–89   Low Risk
      40–69   Medium Risk
      0–39    High Risk
    """

    @staticmethod
    def get_risk_level(score):
        score = float(score)
        if score >= 90:
            return "Safe"
        if score >= 70:
            return "Low Risk"
        if score >= 40:
            return "Medium Risk"
        return "High Risk"

    @staticmethod
    def calculate(current_score, prediction_result, behavior):
        current = float(current_score or 95.0)
        is_anomaly = prediction_result.get("is_anomaly", False)
        action = behavior.get("action_type", "")

        if is_anomaly:
            penalty = 18
            if behavior.get("amount_transferred", 0) > 50000:
                penalty += 10
            if behavior.get("ip_change", 0) == 1:
                penalty += 8
            if behavior.get("failed_attempts", 0) >= 3:
                penalty += 10
            if behavior.get("new_payee_added", 0) == 1:
                penalty += 5
            new_score = max(0, current - penalty)
        else:
            recovery = 3 if action in ("login", "logout") else 5
            new_score = min(100, current + recovery)

        risk_level = TrustScore.get_risk_level(new_score)
        return round(new_score, 2), risk_level
