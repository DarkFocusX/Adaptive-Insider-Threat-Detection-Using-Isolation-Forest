from database.db import get_db


def mark_user_online(user_id):
    """Update last_activity timestamp."""
    from models.user import User

    User.update_last_activity(user_id)


def get_online_users_count():
    db = get_db()
    row = db.execute(
        """
        SELECT COUNT(*) AS c FROM users
        WHERE role = 'user'
          AND last_activity IS NOT NULL
          AND datetime(last_activity) >= datetime('now', '-5 minutes', 'localtime')
        """
    ).fetchone()
    return row["c"] if row else 0


def get_online_users():
    db = get_db()
    rows = db.execute(
        """
        SELECT full_name, email, account_number, trust_score, last_activity
        FROM users
        WHERE role = 'user'
          AND last_activity IS NOT NULL
          AND datetime(last_activity) >= datetime('now', '-5 minutes', 'localtime')
        ORDER BY last_activity DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]
