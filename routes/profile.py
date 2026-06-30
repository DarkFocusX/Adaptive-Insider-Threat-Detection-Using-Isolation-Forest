from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.user import User
from routes.auth import login_required
from security_ai.pipeline import run_security_pipeline

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.get_by_id(session["user_id"])

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name or not phone:
            flash("Name and phone are required.", "danger")
            return render_template("user/profile.html", user=user)

        updated = User.update_profile(user["id"], full_name, phone)
        session["user_name"] = updated["full_name"]
        run_security_pipeline("profile_update")
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.profile"))

    return render_template("user/profile.html", user=user, page_title="Profile")
