from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, AgeTier
from utils.logger import log_auth_attempt, log_demo_access, log_error, log_debug
import os

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        age = request.form.get("age", type=int)

        log_debug(f"Login attempt: username='{username}', age={age}")

        # Check for bypass option
        if os.environ.get("BYPASS_LOGIN") == "true" or username == "bypass":
            log_demo_access("Bypass", 3, "bypass_login")
            session["user_id"] = "bypass"
            session["username"] = username or "Bypass User"
            session["tier_id"] = 3  # Elementary tier
            session["is_demo"] = True
            flash("Login bypassed - full access granted for testing!")
            return redirect(url_for("learning.dashboard"))

        if username and age:
            try:
                # Find or create user
                user = User.query.filter_by(username=username).first()
                if not user:
                    # Auto-assign age tier based on age
                    tier = AgeTier.query.filter(
                        AgeTier.min_age <= age, AgeTier.max_age >= age
                    ).first()

                    if not tier:
                        # Default to elementary tier if no match
                        tier = AgeTier.query.filter_by(name="Elementary").first()

                    user = User(username=username, age=age, tier_id=tier.id if tier else 3)
                    db.session.add(user)
                    db.session.commit()

                session["user_id"] = user.id
                session["username"] = user.username
                session["tier_id"] = user.tier_id

                log_auth_attempt(username, age, True, session_type="regular")
                return redirect(url_for("learning.dashboard"))

            except Exception as e:
                log_error(e, "login_process")
                log_auth_attempt(username, age, False, error=str(e), session_type="regular")
                flash(f"Login error: {str(e)}. Try using 'demo' mode instead.")
        else:
            error_msg = "Please provide both username and age"
            log_auth_attempt(username, age, False, error=error_msg, session_type="regular")
            flash(error_msg)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        age = request.form.get("age", type=int)

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return render_template("auth/register.html")

        # Auto-assign age tier
        tier = AgeTier.query.filter(AgeTier.min_age <= age, AgeTier.max_age >= age).first()

        user = User(username=username, email=email, age=age, tier_id=tier.id if tier else 3)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username
        session["tier_id"] = user.tier_id

        return redirect(url_for("learning.dashboard"))

    return render_template("auth/register.html")


@bp.route("/guest")
def guest_login():
    """Show guest tier selection page"""
    return render_template("auth/guest_select.html")


@bp.route("/start-guest", methods=["POST"])
def start_guest_session():
    """Start a guest session with selected tier"""
    age = request.form.get("age", type=int)
    tier_id = request.form.get("tier_id", type=int)

    if not age or not tier_id:
        flash("Please select an age range to continue")
        return redirect(url_for("auth.guest_login"))

    # Validate tier exists
    tier = AgeTier.query.get(tier_id)
    if not tier:
        flash("Invalid age range selected")
        return redirect(url_for("auth.guest_login"))

    # Create guest session
    session["user_id"] = "guest"
    session["username"] = "Guest User"
    session["tier_id"] = tier_id
    session["age"] = age
    session["is_guest"] = True

    flash(
        f"Welcome, Guest! You're exploring the {tier.name} learning tier. No registration required!"
    )
    return redirect(url_for("learning.dashboard"))


@bp.route("/demo")
def demo():
    """Unified demo access - shows all age tiers to choose from"""
    tier_param = request.args.get("tier", type=int)
    
    # If tier is specified in URL, go directly to that tier
    if tier_param:
        try:
            demo_tier = AgeTier.query.get(tier_param)
            if not demo_tier:
                demo_tier = AgeTier.query.first()  # Fallback

            tier_id = demo_tier.id if demo_tier else 3
            tier_name = demo_tier.name if demo_tier else "Elementary"

            session["user_id"] = "demo"
            session["username"] = "Demo User"
            session["tier_id"] = tier_id
            session["is_demo"] = True

            log_demo_access(tier_name, tier_id, "direct_demo")

            flash(
                f"🎉 Welcome to Bolaquent! You're exploring the {tier_name} tier. "
                f"No signup required - just start learning!"
            )
            return redirect(url_for("learning.dashboard"))

        except Exception as e:
            log_error(e, "demo_setup")
            # Fallback demo session even if database fails
            session["user_id"] = "demo"
            session["username"] = "Demo User"
            session["tier_id"] = 3
            session["is_demo"] = True
            log_demo_access("Elementary", 3, "fallback_demo")
            flash(
                "🎉 Welcome to Bolaquent Demo! Database temporarily unavailable, but you can still explore the interface."
            )
            return redirect(url_for("learning.dashboard"))
    
    # No tier specified - show selection page
    return redirect(url_for("auth.guest_login"))


@bp.route("/quick")
def quick_demo():
    """Ultra-fast demo access for impatient users"""
    session["user_id"] = "quick"
    session["username"] = "Quick Demo"
    session["tier_id"] = 3  # Elementary
    session["is_demo"] = True

    log_demo_access("Elementary", 3, "quick_demo")
    flash("🚀 Quick Demo Active! Exploring Elementary tier vocabulary.")

    return redirect(url_for("learning.dashboard"))
