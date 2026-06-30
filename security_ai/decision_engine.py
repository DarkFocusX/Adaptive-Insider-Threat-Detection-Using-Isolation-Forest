class DecisionEngine:
    """Map trust score to adaptive security actions."""

    @staticmethod
    def evaluate(trust_score):
        score = float(trust_score)

        if score > 90:
            return {
                "access_level": "full",
                "mask_account": False,
                "mask_balance": False,
                "show_decoy_balance": False,
                "disable_transfer": False,
                "disable_withdraw": False,
                "show_warning": False,
                "warning_message": "",
                "generate_alert": False,
            }

        if score >= 70:
            return {
                "access_level": "mask",
                "mask_account": True,
                "mask_balance": False,
                "show_decoy_balance": False,
                "disable_transfer": False,
                "disable_withdraw": False,
                "show_warning": True,
                "warning_message": (
                    "Low risk detected. Sensitive account details are partially masked."
                ),
                "generate_alert": False,
            }

        if score >= 40:
            return {
                "access_level": "decoy",
                "mask_account": True,
                "mask_balance": True,
                "show_decoy_balance": True,
                "disable_transfer": False,
                "disable_withdraw": False,
                "show_warning": True,
                "warning_message": (
                    "Medium risk detected. Decoy data is being shown for your protection."
                ),
                "generate_alert": True,
            }

        return {
            "access_level": "restrict",
            "mask_account": True,
            "mask_balance": True,
            "show_decoy_balance": True,
            "disable_transfer": True,
            "disable_withdraw": True,
            "show_warning": True,
            "warning_message": (
                "High risk detected. Transfers and withdrawals are temporarily restricted."
            ),
            "generate_alert": True,
        }
