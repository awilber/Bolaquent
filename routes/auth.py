from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, AgeTier

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        age = request.form.get("age", type=int)

        if username and age:
            # Find or create user
            user = User.query.filter_by(username=username).first()
            if not user:
                # Auto-assign age tier based on age
                tier = AgeTier.query.filter(AgeTier.min_age <= age, AgeTier.max_age >= age).first()

                if not tier:
                    # Default to elementary tier if no match
                    tier = AgeTier.query.filter_by(name="Elementary").first()

                user = User(username=username, age=age, tier_id=tier.id if tier else 3)
                db.session.add(user)
                db.session.commit()

            session["user_id"] = user.id
            session["username"] = user.username
            session["tier_id"] = user.tier_id

            return redirect(url_for("learning.dashboard"))
        else:
            flash("Please provide both username and age")

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


@bp.route("/demo")
def demo():
    # Create a demo session without requiring registration
    tier_param = request.args.get("tier", type=int)
    
    if tier_param:
        # Use specified tier
        demo_tier = AgeTier.query.get(tier_param)
    else:
        # Default to middle-tier (Educational) for demo
        demo_tier = AgeTier.query.filter_by(name="Elementary").first()
    
    if not demo_tier:
        demo_tier = AgeTier.query.first()  # Fallback to any tier
    
    session["user_id"] = "demo"
    session["username"] = "Demo User"
    session["tier_id"] = demo_tier.id if demo_tier else 3
    session["is_demo"] = True
    
    tier_name = demo_tier.name if demo_tier else "Elementary"
    flash(f"Welcome to the Bolaquent demo! You're experiencing the {tier_name} learning tier. Explore all features without creating an account.")
    return redirect(url_for("learning.dashboard"))
