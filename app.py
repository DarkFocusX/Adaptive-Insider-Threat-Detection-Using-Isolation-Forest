import os

from flask import Flask, redirect, render_template, session, url_for

from config import Config
from database.create_tables import create_tables
from database.db import init_app as init_db
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.deposit import deposit_bp
from routes.logout import logout_bp
from routes.profile import profile_bp
from routes.receipt import receipt_bp
from routes.transaction import transaction_bp
from routes.transfer import transfer_bp
from routes.withdraw import withdraw_bp
from security_ai.adaptive_response import AdaptiveResponse
from security_ai.predict import load_model
from services.online_tracker import mark_user_online


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["LOG_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "ml_model"), exist_ok=True)

    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(deposit_bp)
    app.register_blueprint(withdraw_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(receipt_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.before_request
    def track_session_security():
        if session.get("user_id") and session.get("role") != "admin":
            mark_user_online(session["user_id"])
        if "user_id" in session and "trust_score" not in session:
            session["trust_score"] = 95.0
            session["risk_level"] = "Safe"

    @app.context_processor
    def inject_security_context():
        if session.get("user_id") and session.get("role") != "admin":
            return {"security": AdaptiveResponse.get_display_context(session["user_id"])}
        return {"security": {}}

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    with app.app_context():
        load_model()

    return app


app = create_app()


if __name__ == "__main__":
    create_tables()
    app.run(debug=True, host="0.0.0.0", port=5000)
