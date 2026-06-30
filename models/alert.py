from database.db import get_db


class Alert:
    """Database operations for alerts table."""

    @staticmethod
    def create(user_id, alert_type, severity, message):
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO alerts (user_id, alert_type, severity, message)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, alert_type, severity, message),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_unresolved(limit=50):
        db = get_db()
        rows = db.execute(
            """
            SELECT a.*, u.full_name, u.email, u.account_number
            FROM alerts a
            JOIN users u ON a.user_id = u.id
            WHERE a.is_resolved = 0
            ORDER BY a.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_recent(limit=20):
        db = get_db()
        rows = db.execute(
            """
            SELECT a.*, u.full_name, u.email
            FROM alerts a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def resolve(alert_id):
        db = get_db()
        db.execute(
            "UPDATE alerts SET is_resolved = 1 WHERE id = ?",
            (alert_id,),
        )
        db.commit()
