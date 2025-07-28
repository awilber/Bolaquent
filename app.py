from flask import Flask, render_template, redirect, url_for, session
from flask_cors import CORS
from config import Config
from models import db, AgeTier, VocabularyWord, User
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Create upload directory
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Import and register blueprints
    from routes.auth import bp as auth_bp
    from routes.learning import bp as learning_bp
    from routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(admin_bp)

    # Main routes
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("learning.dashboard"))
        return render_template("index.html")

    @app.route("/init-db")
    def init_db():
        with app.app_context():
            db.create_all()

            # Create age tiers if they don't exist
            if AgeTier.query.count() == 0:
                tiers = [
                    AgeTier(
                        id=1,
                        name="Early Verbal",
                        min_age=2,
                        max_age=4,
                        description="Learning through sensory input and repetition",
                        cognitive_stage="Preoperational (early)",
                        attention_span_minutes=5,
                        words_per_session=5,
                    ),
                    AgeTier(
                        id=2,
                        name="Preschool",
                        min_age=4,
                        max_age=6,
                        description="Language explosion and social play development",
                        cognitive_stage="Preoperational (advanced)",
                        attention_span_minutes=10,
                        words_per_session=8,
                    ),
                    AgeTier(
                        id=3,
                        name="Elementary",
                        min_age=6,
                        max_age=10,
                        description="Logical thinking with concrete objects",
                        cognitive_stage="Concrete Operational",
                        attention_span_minutes=15,
                        words_per_session=12,
                    ),
                    AgeTier(
                        id=4,
                        name="Middle School",
                        min_age=11,
                        max_age=14,
                        description="Abstract thinking development and problem solving",
                        cognitive_stage="Formal Operational (emerging)",
                        attention_span_minutes=25,
                        words_per_session=15,
                    ),
                    AgeTier(
                        id=5,
                        name="High School",
                        min_age=15,
                        max_age=18,
                        description="Advanced abstract reasoning and goal-oriented behavior",
                        cognitive_stage="Formal Operational",
                        attention_span_minutes=30,
                        words_per_session=20,
                    ),
                    AgeTier(
                        id=6,
                        name="Adult",
                        min_age=18,
                        max_age=99,
                        description="Self-directed learning and specialized domain focus",
                        cognitive_stage="Postformal",
                        attention_span_minutes=45,
                        words_per_session=25,
                    ),
                ]

                for tier in tiers:
                    db.session.add(tier)

                # Add sample vocabulary words
                sample_words = [
                    # Early Verbal (Tier 1)
                    VocabularyWord(
                        word="cat",
                        definition="A small furry pet animal",
                        tier_id=1,
                        category="animals",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="red",
                        definition="The color of an apple",
                        tier_id=1,
                        category="colors",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="big",
                        definition="Large in size",
                        tier_id=1,
                        category="descriptors",
                        part_of_speech="adjective",
                    ),
                    # Elementary (Tier 3)
                    VocabularyWord(
                        word="democracy",
                        definition="A system of government by the people",
                        tier_id=3,
                        category="civics",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="photosynthesis",
                        definition="How plants make food from sunlight",
                        tier_id=3,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="multiply",
                        definition="To increase a number by itself several times",
                        tier_id=3,
                        category="math",
                        part_of_speech="verb",
                    ),
                    # Adult (Tier 6)
                    VocabularyWord(
                        word="paradigm",
                        definition="A typical example or pattern of something",
                        tier_id=6,
                        category="academic",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="ubiquitous",
                        definition="Present, appearing, or found everywhere",
                        tier_id=6,
                        category="academic",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="etymology",
                        definition="The origin and historical development of words",
                        tier_id=6,
                        category="linguistics",
                        part_of_speech="noun",
                    ),
                ]

                for word in sample_words:
                    db.session.add(word)

                db.session.commit()
                print("Database initialized with age tiers and sample vocabulary!")

        return redirect(url_for("index"))

    @app.template_filter("datetime")
    def datetime_filter(date):
        if date:
            return date.strftime("%Y-%m-%d %I:%M %p")
        return ""

    # Simple authentication check
    @app.before_request
    def check_auth():
        from flask import request

        # Skip auth for public routes
        public_routes = ["index", "auth.login", "auth.register", "static", "init_db"]
        if request.endpoint in public_routes:
            return

        # Redirect to login if not authenticated
        if (
            "user_id" not in session
            and request.endpoint
            and not request.endpoint.startswith("auth.")
        ):
            return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    print("Creating Bolaquent vocabulary learning app...")
    app = create_app()
    print("Flask app created with learning, auth, and admin blueprints")

    print("Initializing database...")
    with app.app_context():
        db.create_all()
    print("Database initialized")

    # Port management following project patterns
    port = int(os.environ.get("PORT", 5000))

    # Only do port scanning if PORT wasn't explicitly set
    if "PORT" not in os.environ:
        print("PORT not set, scanning for available port...")
        import socket

        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("", port))
                s.close()
                print("Port {} is available".format(port))
                break
            except OSError:
                print("Port {} is occupied, trying next...".format(port))
                port += 10
                if port > 5100:
                    print("No available ports found")
                    exit(1)
        print("Found available port: {}".format(port))
    else:
        print("Using allocated port: {}".format(port))

    print("Starting Bolaquent on port {}".format(port))
    print("Multi-tiered vocabulary learning app accessible at: http://localhost:{}/".format(port))
    print("Features: Age-based learning tiers, Progress tracking, Admin interface")

    app.run(debug=True, host="0.0.0.0", port=port)
