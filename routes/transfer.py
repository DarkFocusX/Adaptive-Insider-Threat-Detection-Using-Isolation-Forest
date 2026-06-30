from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from models.account import Account
from models.transaction import Transaction
from models.user import User
from routes.auth import login_required
from security_ai.adaptive_response import AdaptiveResponse
from security_ai.pipeline import run_security_pipeline

transfer_bp = Blueprint("transfer", __name__)


@transfer_bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    user = User.get_by_id(session["user_id"])
    security = AdaptiveResponse.get_display_context(user["id"])

    if request.method == "POST":
        if security.get("disable_transfer"):
            flash("Transfers are restricted due to elevated security risk.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        receiver_account = request.form.get("receiver_account", "").strip()
        receiver_name = request.form.get("receiver_name", "").strip()
        amount_raw = request.form.get("amount", "").strip()
        description = request.form.get("description", "Fund Transfer").strip()

        if not all([receiver_account, receiver_name, amount_raw]):
            flash("All transfer fields are required.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid transfer amount.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        if receiver_account == user["account_number"]:
            flash("You cannot transfer to your own account.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        receiver = User.get_by_account_number(receiver_account)
        if not receiver:
            flash("Receiver account number not found.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        if amount > user["balance"]:
            flash("Insufficient balance for this transfer.", "danger")
            return render_template("user/transfer.html", user=user, security=security)

        Account.update_balance(user["id"], user["balance"] - amount)
        Account.update_balance(receiver["id"], receiver["balance"] + amount)

        txn = Transaction.create(
            user_id=user["id"],
            transaction_type="Transfer",
            amount=amount,
            description=description or "Fund Transfer",
            receiver_account=receiver_account,
            receiver_name=receiver_name,
        )

        run_security_pipeline("transfer", amount=amount, receiver_account=receiver_account)

        flash(f"₹{amount:.2f} transferred to {receiver_name} successfully.", "success")
        return redirect(url_for("receipt.view_receipt", txn_id=txn["id"]))

    return render_template("user/transfer.html", user=user, security=security)


@transfer_bp.route("/api/lookup-account/<account_number>")
@login_required
def lookup_account(account_number):
    """AJAX helper to auto-fill receiver name."""
    user = User.get_by_id(session["user_id"])
    if account_number == user["account_number"]:
        return jsonify({"success": False, "message": "Cannot transfer to own account"})

    receiver = User.get_by_account_number(account_number)
    if receiver:
        return jsonify({"success": True, "name": receiver["full_name"]})
    return jsonify({"success": False, "message": "Account not found"})
