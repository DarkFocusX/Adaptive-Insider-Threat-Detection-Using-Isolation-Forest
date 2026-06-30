import re
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models.user import User
from security_ai.pipeline import run_security_pipeline

auth_bp = Blueprint("auth", __name__)


def login_required(view_func):
    """Decorator to protect user routes."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([full_name, email, phone, password, confirm_password]):
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            flash("Invalid email format.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if User.email_exists(email):
            flash("Email already registered.", "danger")
            return render_template("auth/register.html")

        user = User.create(
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
            opening_balance=current_app.config["OPENING_BALANCE"],
            trust_score=current_app.config["DEFAULT_TRUST_SCORE"],
        )

        flash(
            f"Registration successful! Your account number is {user['account_number']}.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html")

        user = User.get_by_email(email)

        if not user or not User.verify_password(user, password):
            session["failed_attempts"] = session.get("failed_attempts", 0) + 1
            if user:
                run_security_pipeline(
                    "login_failed",
                    failed_attempt=1,
                    user_id=user["id"],
                )
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if user["role"] == "admin":
            flash("Please use the admin login page.", "warning")
            return render_template("auth/login.html")

        if not user["is_active"]:
            flash("Your account is deactivated. Contact support.", "danger")
            return render_template("auth/login.html")

        session.clear()
        session.permanent = True
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["account_number"] = user["account_number"]
        session["trust_score"] = user["trust_score"]
        session["risk_level"] = user["risk_level"]
        session["login_time"] = datetime.now().isoformat()
        session["download_count"] = 0
        session["known_payees"] = []
        session["failed_attempts"] = 0

        User.update_last_login(user["id"])
        run_security_pipeline("login")

        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(url_for("dashboard.home"))

    return render_template("auth/login.html")
