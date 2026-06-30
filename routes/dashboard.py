from flask import Blueprint, render_template, session

from models.account import Account
from models.transaction import Transaction
from models.user import User
from routes.auth import login_required
from security_ai.adaptive_response import AdaptiveResponse

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    user = User.get_by_id(session["user_id"])
    account = Account.get_account_summary(session["user_id"])
    today_count = Transaction.get_today_count(session["user_id"])
    recent_transactions = Transaction.get_recent(session["user_id"], limit=5)
    security = AdaptiveResponse.get_display_context(session["user_id"])

    return render_template(
        "user/dashboard.html",
        user=user,
        account=account,
        today_count=today_count,
        recent_transactions=recent_transactions,
        security=security,
        page_title="Dashboard",
    )
