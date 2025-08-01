from flask import Flask, render_template, redirect, url_for, session
from flask_cors import CORS
from config import Config
from models import db, AgeTier, VocabularyWord
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

                # Add sample vocabulary words with age-appropriate definitions
                sample_words = [
                    # Early Verbal (Tier 1, Ages 2-3): Basic concrete words, 2-4 word definitions
                    VocabularyWord(
                        word="cat",
                        definition="Pet with fur",
                        tier_id=1,
                        category="animals",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="red",
                        definition="Color like apple",
                        tier_id=1,
                        category="colors",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="big",
                        definition="Very large",
                        tier_id=1,
                        category="descriptors",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="milk",
                        definition="White drink",
                        tier_id=1,
                        category="food",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="go",
                        definition="Move away",
                        tier_id=1,
                        category="actions",
                        part_of_speech="verb",
                    ),
                    VocabularyWord(
                        word="hot",
                        definition="Very warm",
                        tier_id=1,
                        category="descriptors",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="ball",
                        definition="Round toy",
                        tier_id=1,
                        category="toys",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="more",
                        definition="Want extra",
                        tier_id=1,
                        category="requests",
                        part_of_speech="adverb",
                    ),
                    VocabularyWord(
                        word="up",
                        definition="Go higher",
                        tier_id=1,
                        category="directions",
                        part_of_speech="adverb",
                    ),
                    VocabularyWord(
                        word="bye",
                        definition="See you later",
                        tier_id=1,
                        category="social",
                        part_of_speech="interjection",
                    ),
                    # Preschool (Tier 2, Ages 4-5): Expanded vocabulary, 4-6 word definitions
                    VocabularyWord(
                        word="happy",
                        definition="Feeling good and smiling",
                        tier_id=2,
                        category="emotions",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="friend",
                        definition="Someone you like to play with",
                        tier_id=2,
                        category="social",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="scared",
                        definition="Feeling afraid of something",
                        tier_id=2,
                        category="emotions",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="share",
                        definition="Let others use your things",
                        tier_id=2,
                        category="social",
                        part_of_speech="verb",
                    ),
                    VocabularyWord(
                        word="count",
                        definition="Say numbers in order",
                        tier_id=2,
                        category="math",
                        part_of_speech="verb",
                    ),
                    VocabularyWord(
                        word="circle",
                        definition="Round shape like a ball",
                        tier_id=2,
                        category="shapes",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="family",
                        definition="People who live together and care",
                        tier_id=2,
                        category="social",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="rainbow",
                        definition="Pretty colors in the sky",
                        tier_id=2,
                        category="nature",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="gentle",
                        definition="Being soft and kind",
                        tier_id=2,
                        category="behavior",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="listen",
                        definition="Use your ears to hear",
                        tier_id=2,
                        category="actions",
                        part_of_speech="verb",
                    ),
                    # Elementary (Tier 3, Ages 6-10): Academic foundation, age-appropriate explanations
                    VocabularyWord(
                        word="community",
                        definition="A group of people living in the same area who help each other",
                        tier_id=3,
                        category="social studies",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="habitat",
                        definition="The natural home where an animal lives and finds food",
                        tier_id=3,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="addition",
                        definition="Putting numbers together to find the total amount",
                        tier_id=3,
                        category="math",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="character",
                        definition="A person or animal in a story or book",
                        tier_id=3,
                        category="reading",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="season",
                        definition="One of the four parts of the year like spring or winter",
                        tier_id=3,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="continent",
                        definition="A very large area of land like North America or Africa",
                        tier_id=3,
                        category="geography",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="compare",
                        definition="Look at two things to see how they are the same or different",
                        tier_id=3,
                        category="thinking",
                        part_of_speech="verb",
                    ),
                    VocabularyWord(
                        word="mammal",
                        definition="An animal that feeds milk to its babies and has warm blood",
                        tier_id=3,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="pattern",
                        definition="Something that repeats in the same way over and over",
                        tier_id=3,
                        category="math",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="opinion",
                        definition="What you think about something, not a fact",
                        tier_id=3,
                        category="thinking",
                        part_of_speech="noun",
                    ),
                    # Middle School (Tier 4, Ages 11-14): Abstract concepts, detailed explanations
                    VocabularyWord(
                        word="democracy",
                        definition="A system of government where people vote to choose their leaders and make decisions",
                        tier_id=4,
                        category="civics",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="ecosystem",
                        definition="All the living and non-living things in an area that depend on each other",
                        tier_id=4,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="fraction",
                        definition="A number that represents part of a whole, like 1/2 or 3/4",
                        tier_id=4,
                        category="math",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="metaphor",
                        definition="A way of describing something by comparing it to something else without using 'like' or 'as'",
                        tier_id=4,
                        category="language arts",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="culture",
                        definition="The beliefs, customs, arts, and way of life of a group of people",
                        tier_id=4,
                        category="social studies",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="hypothesis",
                        definition="An educated guess about what will happen in a scientific experiment",
                        tier_id=4,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="variable",
                        definition="Something that can change or be changed in an experiment or equation",
                        tier_id=4,
                        category="math",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="symbolism",
                        definition="Using objects or actions to represent deeper meanings or ideas",
                        tier_id=4,
                        category="literature",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="revolution",
                        definition="A complete change in the way people think about or do something",
                        tier_id=4,
                        category="history",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="perspective",
                        definition="A particular way of looking at or thinking about something",
                        tier_id=4,
                        category="thinking",
                        part_of_speech="noun",
                    ),
                    # High School (Tier 5, Ages 15-18): Advanced academic vocabulary, comprehensive explanations
                    VocabularyWord(
                        word="paradigm",
                        definition="A typical example or model that serves as a pattern for understanding concepts",
                        tier_id=5,
                        category="academic",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="synthesis",
                        definition="The combination of separate elements or ideas to form a connected whole",
                        tier_id=5,
                        category="academic",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="rhetoric",
                        definition="The art of effective or persuasive speaking and writing, especially in public",
                        tier_id=5,
                        category="language arts",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="globalization",
                        definition="The process by which businesses and cultures develop international influence",
                        tier_id=5,
                        category="social studies",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="catalyst",
                        definition="Something that causes or accelerates a change or reaction",
                        tier_id=5,
                        category="science",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="allegory",
                        definition="A story with hidden meaning where characters represent ideas or principles",
                        tier_id=5,
                        category="literature",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="autonomous",
                        definition="Having the freedom to act independently and make one's own decisions",
                        tier_id=5,
                        category="academic",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="empirical",
                        definition="Based on observation and experience rather than theory or pure logic",
                        tier_id=5,
                        category="science",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="ideology",
                        definition="A system of ideas and beliefs that forms the basis of political or economic theory",
                        tier_id=5,
                        category="social studies",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="juxtaposition",
                        definition="Placing two contrasting elements side by side to highlight their differences",
                        tier_id=5,
                        category="literature",
                        part_of_speech="noun",
                    ),
                    # Adult (Tier 6, Ages 18+): Professional and sophisticated vocabulary, full academic definitions
                    VocabularyWord(
                        word="ubiquitous",
                        definition="Present, appearing, or found everywhere; omnipresent in a pervasive manner",
                        tier_id=6,
                        category="academic",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="etymology",
                        definition="The study of the origin and historical development of words and their meanings",
                        tier_id=6,
                        category="linguistics",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="epistemology",
                        definition="The branch of philosophy concerned with the theory of knowledge and justified belief",
                        tier_id=6,
                        category="philosophy",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="hegemony",
                        definition="Leadership or dominance, especially by one social group over others",
                        tier_id=6,
                        category="sociology",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="nomenclature",
                        definition="The devising or choosing of names for things, especially in scientific classification",
                        tier_id=6,
                        category="academic",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="paradigmatic",
                        definition="Serving as a typical example or model of something; representative of a paradigm",
                        tier_id=6,
                        category="academic",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="hermeneutics",
                        definition="The method and theory of interpretation, especially of scriptural and literary texts",
                        tier_id=6,
                        category="philosophy",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="ontological",
                        definition="Relating to the nature of being, existence, or reality as a philosophical concept",
                        tier_id=6,
                        category="philosophy",
                        part_of_speech="adjective",
                    ),
                    VocabularyWord(
                        word="phenomenology",
                        definition="The philosophical study of structures of experience and consciousness",
                        tier_id=6,
                        category="philosophy",
                        part_of_speech="noun",
                    ),
                    VocabularyWord(
                        word="teleological",
                        definition="Relating to or involving the explanation of phenomena by their purposes rather than causes",
                        tier_id=6,
                        category="philosophy",
                        part_of_speech="adjective",
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
