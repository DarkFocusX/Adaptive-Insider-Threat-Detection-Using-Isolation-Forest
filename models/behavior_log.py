from database.db import get_db


class BehaviorLog:
    """Database operations for behavior_logs table."""

    @staticmethod
    def create(
        user_id,
        action_type,
        features,
        prediction,
        trust_score,
        ip_address=None,
        risk_level=None,
        decision=None,
        model_used=None,
        anomaly_score=None,
    ):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO behavior_logs (
                user_id, action_type,
                login_hour, session_duration, transaction_count,
                amount_transferred, download_count, ip_change,
                new_payee_added, failed_attempts,
                ip_address, prediction, trust_score,
                risk_level, decision, model_used, anomaly_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                action_type,
                features["login_hour"],
                features["session_duration"],
                features["transaction_count"],
                features["amount_transferred"],
                features["download_count"],
                features["ip_change"],
                features["new_payee_added"],
                features["failed_attempts"],
                ip_address,
                prediction,
                trust_score,
                risk_level,
                decision,
                model_used,
                anomaly_score,
            ),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_recent(user_id, limit=20):
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM behavior_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all(limit=100):
        db = get_db()
        rows = db.execute(
            """
            SELECT bl.*, u.full_name, u.email
            FROM behavior_logs bl
            JOIN users u ON bl.user_id = u.id
            ORDER BY bl.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def count_today_transactions(user_id):
        db = get_db()
        row = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM transactions
            WHERE user_id = ?
              AND DATE(created_at) = DATE('now', 'localtime')
            """,
            (user_id,),
        ).fetchone()
        return row["count"] if row else 0
