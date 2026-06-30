import random

from flask import session

from models.user import User


class AdaptiveResponse:
    """Apply decision-engine output to session + display helpers."""

    @staticmethod
    def apply(trust_score, risk_level, decision):
        session["trust_score"] = trust_score
        session["risk_level"] = risk_level
        session["security_decision"] = decision

        if decision.get("show_decoy_balance"):
            session["decoy_balance"] = round(random.uniform(5000, 50000), 2)
        else:
            session.pop("decoy_balance", None)

    @staticmethod
    def mask_account_number(account_number):
        account_number = str(account_number or "")
        if len(account_number) <= 4:
            return "****"
        return f"****{account_number[-4:]}"

    @staticmethod
    def get_display_context(user_id):
        user = User.get_by_id(user_id)
        if not user:
            return {}

        decision = session.get("security_decision") or {}
        trust_score = float(session.get("trust_score", user.get("trust_score", 95)))
        real_balance = float(user.get("balance", 0))

        display_account = user["account_number"]
        display_balance = real_balance

        if decision.get("mask_account"):
            display_account = AdaptiveResponse.mask_account_number(user["account_number"])

        if decision.get("show_decoy_balance"):
            display_balance = float(session.get("decoy_balance", real_balance * 0.6))
        elif decision.get("mask_balance"):
            display_balance = None

        return {
            "trust_score": trust_score,
            "risk_level": session.get("risk_level", user.get("risk_level", "Safe")),
            "decision": decision,
            "display_account": display_account,
            "display_balance": display_balance,
            "real_balance": real_balance,
            "disable_transfer": decision.get("disable_transfer", False),
            "disable_withdraw": decision.get("disable_withdraw", False),
            "show_warning": decision.get("show_warning", False),
            "warning_message": decision.get("warning_message", ""),
            "last_prediction": session.get("last_prediction", "Normal"),
        }
