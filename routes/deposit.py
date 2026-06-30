from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.account import Account
from models.transaction import Transaction
from models.user import User
from routes.auth import login_required
from security_ai.pipeline import run_security_pipeline

deposit_bp = Blueprint("deposit", __name__)


@deposit_bp.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    user = User.get_by_id(session["user_id"])

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        description = request.form.get("description", "Cash Deposit").strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid deposit amount.", "danger")
            return render_template("user/deposit.html", user=user)

        new_balance = user["balance"] + amount
        Account.update_balance(user["id"], new_balance)

        txn = Transaction.create(
            user_id=user["id"],
            transaction_type="Deposit",
            amount=amount,
            description=description or "Cash Deposit",
        )

        run_security_pipeline("deposit", amount=amount)

        flash(f"₹{amount:.2f} deposited successfully.", "success")
        return redirect(url_for("receipt.view_receipt", txn_id=txn["id"]))

    return render_template("user/deposit.html", user=user)
