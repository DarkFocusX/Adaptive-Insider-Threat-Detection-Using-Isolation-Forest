import io

from flask import Blueprint, flash, redirect, render_template, send_file, session, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.transaction import Transaction
from routes.auth import login_required
from security_ai.pipeline import run_security_pipeline

receipt_bp = Blueprint("receipt", __name__)


def build_receipt_pdf(txn):
    """Generate PDF receipt bytes using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>SecureBank AI — Transaction Receipt</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    data = [
        ["Transaction ID", txn["transaction_id"]],
        ["Type", txn["transaction_type"]],
        ["Sender", f"{txn['sender_name']} ({txn['sender_account']})"],
        ["Receiver", txn.get("receiver_name") or "—"],
        ["Receiver Account", txn.get("receiver_account") or "—"],
        ["Amount", f"₹{txn['amount']:.2f}"],
        ["Date", str(txn["created_at"])],
        ["Status", txn["status"]],
        ["Description", txn.get("description") or "—"],
    ]

    table = Table(data, colWidths=[160, 340])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.whitesmoke),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for banking with SecureBank AI.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


@receipt_bp.route("/receipt/<int:txn_id>")
@login_required
def view_receipt(txn_id):
    txn = Transaction.get_by_db_id(txn_id)

    if not txn or txn["user_id"] != session["user_id"]:
        flash("Receipt not found.", "danger")
        return redirect(url_for("transaction.history"))

    return render_template("user/receipt.html", txn=txn, page_title="Receipt")


@receipt_bp.route("/receipt/<int:txn_id>/download")
@login_required
def download_receipt(txn_id):
    txn = Transaction.get_by_db_id(txn_id)

    if not txn or txn["user_id"] != session["user_id"]:
        flash("Receipt not found.", "danger")
        return redirect(url_for("transaction.history"))

    run_security_pipeline("receipt_download", is_download=True)

    pdf_buffer = build_receipt_pdf(txn)
    filename = f"{txn['transaction_id']}_receipt.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )
