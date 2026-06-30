import sqlite3

from flask import current_app, g


def get_db():
    """Return a SQLite connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_e=None):
    """Close SQLite connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register teardown with Flask app."""
    app.teardown_appcontext(close_db)
