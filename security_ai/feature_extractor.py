import numpy as np

FEATURE_ORDER = [
    "login_hour",
    "session_duration",
    "transaction_count",
    "amount_transferred",
    "download_count",
    "ip_change",
    "new_payee_added",
    "failed_attempts",
]


class FeatureExtractor:
    """Convert behavior dict into ML feature vector."""

    @staticmethod
    def to_vector(behavior):
        if not behavior:
            return np.array([[0, 0, 0, 0, 0, 0, 0, 0]], dtype=float)

        vector = [float(behavior.get(name, 0)) for name in FEATURE_ORDER]
        return np.array([vector], dtype=float)

    @staticmethod
    def explain(behavior):
        """Human-readable feature map for logs/admin UI."""
        return {name: behavior.get(name, 0) for name in FEATURE_ORDER}
