from flask import Blueprint, render_template, request, session

from models.transaction import Transaction
from routes.auth import login_required

transaction_bp = Blueprint("transaction", __name__)


@transaction_bp.route("/transactions")
@login_required
def history():
    search = request.args.get("search", "").strip()
    trans_type = request.args.get("type", "").strip()
    page = request.args.get("page", 1)

    result = Transaction.get_user_transactions(
        user_id=session["user_id"],
        search=search,
        trans_type=trans_type,
        page=page,
        per_page=10,
    )

    return render_template(
        "user/transaction_history.html",
        transactions=result["transactions"],
        total=result["total"],
        page=result["page"],
        total_pages=result["total_pages"],
        search=search,
        trans_type=trans_type,
        page_title="Transaction History",
    )
