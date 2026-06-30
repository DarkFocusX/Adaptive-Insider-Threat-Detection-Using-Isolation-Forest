from database.db import get_db


class Account:
    """Account-related operations (balance, trust score)."""

    @staticmethod
    def get_balance(user_id):
        db = get_db()
        row = db.execute(
            "SELECT balance FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return float(row["balance"]) if row else 0.0

    @staticmethod
    def update_balance(user_id, new_balance):
        db = get_db()
        db.execute(
            "UPDATE users SET balance = ? WHERE id = ?",
            (new_balance, user_id),
        )
        db.commit()

    @staticmethod
    def update_trust_score(user_id, trust_score, risk_level):
        db = get_db()
        db.execute(
            """
            UPDATE users
            SET trust_score = ?, risk_level = ?
            WHERE id = ?
            """,
            (trust_score, risk_level, user_id),
        )
        db.commit()

    @staticmethod
    def get_account_summary(user_id):
        db = get_db()
        row = db.execute(
            """
            SELECT account_number, balance, trust_score, risk_level
            FROM users WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
