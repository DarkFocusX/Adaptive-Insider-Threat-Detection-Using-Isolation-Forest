import random
import string

from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db


class User:
    """User model for registration, login, and profile operations."""

    @staticmethod
    def generate_account_number():
        """Generate a unique 12-digit account number."""
        db = get_db()
        while True:
            number = "".join(random.choices(string.digits, k=12))
            exists = db.execute(
                "SELECT id FROM users WHERE account_number = ?", (number,)
            ).fetchone()
            if not exists:
                return number

    @staticmethod
    def create(full_name, email, phone, password, opening_balance, trust_score):
        """Register a new user."""
        db = get_db()
        password_hash = generate_password_hash(password)
        account_number = User.generate_account_number()

        db.execute(
            """
            INSERT INTO users (
                full_name, email, phone, password_hash,
                account_number, balance, trust_score, risk_level, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name.strip(),
                email.strip().lower(),
                phone.strip(),
                password_hash,
                account_number,
                opening_balance,
                trust_score,
                "Safe",
                "user",
            ),
        )
        db.commit()
        return User.get_by_email(email)

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_account_number(account_number):
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE account_number = ?", (account_number,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def email_exists(email):
        db = get_db()
        row = db.execute(
            "SELECT id FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return row is not None

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user["password_hash"], password)

    @staticmethod
    def update_last_login(user_id):
        db = get_db()
        db.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        db.commit()

    @staticmethod
    def update_last_activity(user_id):
        db = get_db()
        db.execute(
            "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        db.commit()

    @staticmethod
    def update_profile(user_id, full_name, phone):
        db = get_db()
        db.execute(
            """
            UPDATE users
            SET full_name = ?, phone = ?
            WHERE id = ?
            """,
            (full_name.strip(), phone.strip(), user_id),
        )
        db.commit()
        return User.get_by_id(user_id)

    @staticmethod
    def get_all_users():
        db = get_db()
        rows = db.execute(
            """
            SELECT id, full_name, email, phone, account_number,
                   balance, trust_score, risk_level, role, is_active,
                   created_at, last_login, last_activity
            FROM users
            WHERE role = 'user'
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_admin_stats():
        db = get_db()
        stats = {}
        stats["total_users"] = db.execute(
            "SELECT COUNT(*) AS c FROM users WHERE role = 'user'"
        ).fetchone()["c"]
        stats["high_risk_users"] = db.execute(
            """
            SELECT COUNT(*) AS c FROM users
            WHERE role = 'user' AND (trust_score < 40 OR risk_level = 'High Risk')
            """
        ).fetchone()["c"]
        stats["avg_trust_score"] = db.execute(
            "SELECT AVG(trust_score) AS avg FROM users WHERE role = 'user'"
        ).fetchone()["avg"] or 0
        stats["total_alerts"] = db.execute(
            "SELECT COUNT(*) AS c FROM alerts WHERE is_resolved = 0"
        ).fetchone()["c"]
        stats["total_predictions"] = db.execute(
            "SELECT COUNT(*) AS c FROM behavior_logs"
        ).fetchone()["c"]
        stats["anomaly_count"] = db.execute(
            "SELECT COUNT(*) AS c FROM behavior_logs WHERE prediction = 'Anomaly'"
        ).fetchone()["c"]
        return stats

    @staticmethod
    def get_trust_distribution():
        db = get_db()
        buckets = [
            ("90-100 (Safe)", 90, 101),
            ("70-89 (Low Risk)", 70, 90),
            ("40-69 (Medium Risk)", 40, 70),
            ("0-39 (High Risk)", 0, 40),
        ]
        result = []
        for label, low, high in buckets:
            count = db.execute(
                """
                SELECT COUNT(*) AS c FROM users
                WHERE role = 'user' AND trust_score >= ? AND trust_score < ?
                """,
                (low, high),
            ).fetchone()["c"]
            result.append({"label": label, "count": count})
        return result

    @staticmethod
    def get_risk_distribution():
        db = get_db()
        levels = ["Safe", "Low Risk", "Medium Risk", "High Risk"]
        return [
            {
                "label": level,
                "count": db.execute(
                    "SELECT COUNT(*) AS c FROM users WHERE role = 'user' AND risk_level = ?",
                    (level,),
                ).fetchone()["c"],
            }
            for level in levels
        ]

    @staticmethod
    def get_adaptive_users():
        """Users currently under adaptive security (trust <= 90)."""
        db = get_db()
        rows = db.execute(
            """
            SELECT id, full_name, email, account_number, trust_score, risk_level
            FROM users
            WHERE role = 'user' AND trust_score <= 90
            ORDER BY trust_score ASC
            """
        ).fetchall()
        users = []
        for row in rows:
            u = dict(row)
            score = float(u["trust_score"])
            if score > 90:
                u["adaptive_mode"] = "Full Access"
            elif score >= 70:
                u["adaptive_mode"] = "Mask Data"
            elif score >= 40:
                u["adaptive_mode"] = "Decoy Data"
            else:
                u["adaptive_mode"] = "Restrict Transfer/Withdraw"
            users.append(u)
        return users
