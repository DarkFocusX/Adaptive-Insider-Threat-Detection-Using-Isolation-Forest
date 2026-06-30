from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.account import Account
from models.transaction import Transaction
from models.user import User
from routes.auth import login_required
from security_ai.adaptive_response import AdaptiveResponse
from security_ai.pipeline import run_security_pipeline

withdraw_bp = Blueprint("withdraw", __name__)


@withdraw_bp.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    user = User.get_by_id(session["user_id"])
    security = AdaptiveResponse.get_display_context(user["id"])

    if request.method == "POST":
        if security.get("disable_withdraw"):
            flash("Withdrawals are restricted due to elevated security risk.", "danger")
            return render_template("user/withdraw.html", user=user, security=security)

        amount = request.form.get("amount", "").strip()
        description = request.form.get("description", "Cash Withdrawal").strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid withdrawal amount.", "danger")
            return render_template("user/withdraw.html", user=user, security=security)

        if amount > user["balance"]:
            flash("Insufficient balance for this withdrawal.", "danger")
            return render_template("user/withdraw.html", user=user, security=security)

        new_balance = user["balance"] - amount
        Account.update_balance(user["id"], new_balance)

        txn = Transaction.create(
            user_id=user["id"],
            transaction_type="Withdraw",
            amount=amount,
            description=description or "Cash Withdrawal",
        )

        run_security_pipeline("withdraw", amount=amount)

        flash(f"₹{amount:.2f} withdrawn successfully.", "success")
        return redirect(url_for("receipt.view_receipt", txn_id=txn["id"]))

    return render_template("user/withdraw.html", user=user, security=security)
