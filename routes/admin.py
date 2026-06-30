from functools import wraps

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from models.alert import Alert
from models.behavior_log import BehaviorLog
from models.user import User
from security_ai.decision_engine import DecisionEngine
from security_ai.predict import model_status
from services.online_tracker import get_online_users, get_online_users_count

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("admin_id") != session.get("user_id") or session.get("role") != "admin":
            flash("Admin access required.", "warning")
            return redirect(url_for("admin.admin_login"))
        return view_func(*args, **kwargs)

    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.get_by_email(email)
        if not user or user["role"] != "admin":
            flash("Invalid admin credentials.", "danger")
            return render_template("admin/admin_login.html")

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid admin credentials.", "danger")
            return render_template("admin/admin_login.html")

        session.clear()
        session.permanent = True
        session["user_id"] = user["id"]
        session["admin_id"] = user["id"]
        session["role"] = "admin"
        session["user_name"] = user["full_name"]

        flash("Welcome, Admin.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/admin_login.html")


@admin_bp.route("/logout")
def admin_logout():
    session.clear()
    flash("Admin logged out.", "info")
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    stats = User.get_admin_stats()
    stats["online_users"] = get_online_users_count()
    stats["avg_trust_score"] = round(float(stats["avg_trust_score"]), 2)

    return render_template(
        "admin/admin_dashboard.html",
        stats=stats,
        model_status=model_status(),
        recent_alerts=Alert.get_recent(8),
        recent_logs=BehaviorLog.get_all(8),
        page_title="Admin Dashboard",
    )


@admin_bp.route("/users")
@admin_required
def users():
    return render_template(
        "admin/users.html",
        users=User.get_all_users(),
        online_users=get_online_users(),
        page_title="Users",
    )


@admin_bp.route("/alerts")
@admin_required
def alerts():
    show = request.args.get("show", "unresolved")
    if show == "all":
        alerts_list = Alert.get_recent(100)
    else:
        alerts_list = Alert.get_unresolved(100)

    return render_template(
        "admin/alerts.html",
        alerts=alerts_list,
        show=show,
        page_title="Alerts",
    )


@admin_bp.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
@admin_required
def resolve_alert(alert_id):
    Alert.resolve(alert_id)
    flash("Alert marked as resolved.", "success")
    return redirect(url_for("admin.alerts"))


@admin_bp.route("/logs")
@admin_required
def logs():
    return render_template(
        "admin/logs.html",
        logs=BehaviorLog.get_all(200),
        page_title="Activity Logs",
    )


@admin_bp.route("/trust-scores")
@admin_required
def trust_scores():
    users = User.get_adaptive_users()
    all_users = User.get_all_users()

    enriched = []
    for u in all_users:
        decision = DecisionEngine.evaluate(float(u["trust_score"]))
        enriched.append({**u, "decision": decision})

    return render_template(
        "admin/trust_score.html",
        adaptive_users=users,
        users=enriched,
        page_title="Trust Scores",
    )


@admin_bp.route("/api/charts/trust-distribution")
@admin_required
def chart_trust_distribution():
    data = User.get_trust_distribution()
    return jsonify({
        "labels": [d["label"] for d in data],
        "values": [d["count"] for d in data],
    })


@admin_bp.route("/api/charts/risk-distribution")
@admin_required
def chart_risk_distribution():
    data = User.get_risk_distribution()
    return jsonify({
        "labels": [d["label"] for d in data],
        "values": [d["count"] for d in data],
    })


@admin_bp.route("/api/charts/user-activity")
@admin_required
def chart_user_activity():
    from database.db import get_db

    db = get_db()
    rows = db.execute(
        """
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM behavior_logs
        WHERE created_at >= datetime('now', '-7 days', 'localtime')
        GROUP BY DATE(created_at)
        ORDER BY day ASC
        """
    ).fetchall()
    return jsonify({
        "labels": [r["day"] for r in rows],
        "values": [r["count"] for r in rows],
    })


@admin_bp.route("/api/charts/predictions")
@admin_required
def chart_predictions():
    from database.db import get_db

    db = get_db()
    normal = db.execute(
        "SELECT COUNT(*) AS c FROM behavior_logs WHERE prediction = 'Normal'"
    ).fetchone()["c"]
    anomaly = db.execute(
        "SELECT COUNT(*) AS c FROM behavior_logs WHERE prediction = 'Anomaly'"
    ).fetchone()["c"]
    return jsonify({
        "labels": ["Normal", "Anomaly"],
        "values": [normal, anomaly],
    })
