from flask import Blueprint, flash, redirect, session, url_for

from security_ai.pipeline import run_security_pipeline

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout():
    if session.get("user_id"):
        run_security_pipeline("logout")
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
