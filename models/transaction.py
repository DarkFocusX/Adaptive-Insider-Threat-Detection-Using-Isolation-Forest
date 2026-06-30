import uuid
from datetime import datetime

from database.db import get_db


class Transaction:
    """Transaction model for deposit, withdraw, and transfer operations."""

    @staticmethod
    def generate_transaction_id():
        """Generate a unique transaction reference ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique = uuid.uuid4().hex[:6].upper()
        return f"TXN{timestamp}{unique}"

    @staticmethod
    def create(
        user_id,
        transaction_type,
        amount,
        description=None,
        receiver_account=None,
        receiver_name=None,
        status="Completed",
    ):
        """Insert a new transaction record."""
        db = get_db()
        transaction_id = Transaction.generate_transaction_id()

        cursor = db.execute(
            """
            INSERT INTO transactions (
                user_id, transaction_type, amount, description,
                receiver_account, receiver_name, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                transaction_type,
                float(amount),
                description,
                receiver_account,
                receiver_name,
                status,
            ),
        )
        db.commit()

        return Transaction.get_by_id(cursor.lastrowid, transaction_id=transaction_id)

    @staticmethod
    def get_by_id(db_id, transaction_id=None):
        db = get_db()
        row = db.execute(
            """
            SELECT t.*, u.full_name AS sender_name, u.account_number AS sender_account
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.id = ?
            """,
            (db_id,),
        ).fetchone()

        if not row:
            return None

        data = dict(row)
        data["transaction_id"] = transaction_id or f"TXN{data['id']:08d}"
        return data

    @staticmethod
    def get_by_db_id(db_id):
        return Transaction.get_by_id(db_id)

    @staticmethod
    def get_user_transactions(user_id, search="", trans_type="", page=1, per_page=10):
        """Fetch paginated transactions with optional search and filter."""
        db = get_db()
        page = max(1, int(page))
        per_page = max(1, min(50, int(per_page)))
        offset = (page - 1) * per_page

        query = """
            SELECT t.*, u.full_name AS sender_name, u.account_number AS sender_account
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ?
        """
        params = [user_id]

        if search:
            query += (
                " AND (t.description LIKE ? OR t.receiver_name LIKE ? "
                "OR t.receiver_account LIKE ?)"
            )
            like = f"%{search}%"
            params.extend([like, like, like])

        if trans_type:
            query += " AND t.transaction_type = ?"
            params.append(trans_type)

        count_query = query.replace(
            "SELECT t.*, u.full_name AS sender_name, u.account_number AS sender_account",
            "SELECT COUNT(*) AS total",
        )
        total = db.execute(count_query, params).fetchone()["total"]

        query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        rows = db.execute(query, params).fetchall()
        transactions = []
        for row in rows:
            item = dict(row)
            item["transaction_id"] = f"TXN{item['id']:08d}"
            transactions.append(item)

        return {
            "transactions": transactions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": max(1, (total + per_page - 1) // per_page),
        }

    @staticmethod
    def get_today_count(user_id):
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

    @staticmethod
    def get_recent(user_id, limit=5):
        db = get_db()
        rows = db.execute(
            """
            SELECT t.*, u.full_name AS sender_name, u.account_number AS sender_account
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

        results = []
        for row in rows:
            item = dict(row)
            item["transaction_id"] = f"TXN{item['id']:08d}"
            results.append(item)
        return results
