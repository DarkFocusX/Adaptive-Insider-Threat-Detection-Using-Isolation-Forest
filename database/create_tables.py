import sqlite3

from werkzeug.security import generate_password_hash

from config import Config


def create_tables(db_path=None):
    """Create all SQLite tables for the project."""
    db_path = db_path or Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            account_number TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL DEFAULT 0,
            trust_score REAL NOT NULL DEFAULT 95,
            risk_level TEXT NOT NULL DEFAULT 'Safe',
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            last_activity TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            receiver_account TEXT,
            receiver_name TEXT,
            status TEXT NOT NULL DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS behavior_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            login_hour INTEGER,
            session_duration REAL,
            transaction_count INTEGER,
            amount_transferred REAL,
            download_count INTEGER,
            ip_change INTEGER,
            new_payee_added INTEGER,
            failed_attempts INTEGER,
            ip_address TEXT,
            prediction TEXT,
            trust_score REAL,
            risk_level TEXT,
            decision TEXT,
            model_used TEXT,
            anomaly_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            is_resolved INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    migrations = [
        ("users", "last_activity", "ALTER TABLE users ADD COLUMN last_activity TIMESTAMP"),
        ("behavior_logs", "risk_level", "ALTER TABLE behavior_logs ADD COLUMN risk_level TEXT"),
        ("behavior_logs", "decision", "ALTER TABLE behavior_logs ADD COLUMN decision TEXT"),
        ("behavior_logs", "model_used", "ALTER TABLE behavior_logs ADD COLUMN model_used TEXT"),
        ("behavior_logs", "anomaly_score", "ALTER TABLE behavior_logs ADD COLUMN anomaly_score REAL"),
    ]
    for table, column, sql in migrations:
        existing = [
            row[1]
            for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()
        ]
        if column not in existing:
            cursor.execute(sql)

    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO users (
                full_name, email, phone, password_hash,
                account_number, balance, trust_score, risk_level, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "System Admin",
                "admin@bank.local",
                "9999999999",
                generate_password_hash("Admin@123"),
                "ADMIN00001",
                0.0,
                100.0,
                "Safe",
                "admin",
            ),
        )

    conn.commit()
    conn.close()
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()
