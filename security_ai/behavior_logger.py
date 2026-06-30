from datetime import datetime

from flask import request, session

from models.behavior_log import BehaviorLog


class BehaviorLogger:
    """
    Collect behavioral signals for each banking operation.
    Triggered on: login, deposit, withdraw, transfer, logout, receipt download.
    """

    @staticmethod
    def _get_client_ip():
        return request.headers.get("X-Forwarded-For", request.remote_addr) or "127.0.0.1"

    @staticmethod
    def _session_duration_minutes():
        login_time = session.get("login_time")
        if not login_time:
            return 0.0
        try:
            start = datetime.fromisoformat(login_time)
            return round((datetime.now() - start).total_seconds() / 60.0, 2)
        except ValueError:
            return 0.0

    @staticmethod
    def _detect_ip_change():
        current_ip = BehaviorLogger._get_client_ip()
        last_ip = session.get("last_ip")
        session["last_ip"] = current_ip
        if not last_ip:
            return 0
        return 1 if current_ip != last_ip else 0

    @staticmethod
    def _is_new_payee(receiver_account):
        if not receiver_account:
            return 0
        payees = session.setdefault("known_payees", [])
        if receiver_account in payees:
            return 0
        payees.append(receiver_account)
        session["known_payees"] = payees
        return 1

    @staticmethod
    def collect(
        action_type,
        amount=0.0,
        receiver_account=None,
        is_download=False,
        failed_attempt=0,
        user_id=None,
    ):
        """Build raw behavior dictionary before ML feature extraction."""
        user_id = user_id or session.get("user_id")
        if not user_id:
            return None

        if is_download:
            session["download_count"] = session.get("download_count", 0) + 1

        if failed_attempt:
            session["failed_attempts"] = session.get("failed_attempts", 0) + 1

        transaction_count = BehaviorLog.count_today_transactions(user_id)

        return {
            "action_type": action_type,
            "login_hour": datetime.now().hour,
            "session_duration": BehaviorLogger._session_duration_minutes(),
            "transaction_count": transaction_count,
            "amount_transferred": float(amount or 0),
            "download_count": int(session.get("download_count", 0)),
            "ip_change": BehaviorLogger._detect_ip_change(),
            "new_payee_added": BehaviorLogger._is_new_payee(receiver_account),
            "failed_attempts": int(session.get("failed_attempts", 0)),
            "ip_address": BehaviorLogger._get_client_ip(),
        }
