from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models import db, User, VocabularyWord, UserProgress
from datetime import datetime

bp = Blueprint("learning", __name__, url_prefix="/learning")


@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Handle demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        tier_id = session.get("tier_id", 3)  # Default to Elementary
        total_words = VocabularyWord.query.filter_by(tier_id=tier_id).count()
        learned_words = 8  # Mock progress for demo/guest
        progress_percentage = (learned_words / total_words * 100) if total_words > 0 else 0

        # Create mock user object
        mock_user = type(
            "obj",
            (object,),
            {
                "username": session.get("username", "Guest User"), 
                "tier_id": tier_id,
                "age": session.get("age", 8),  # Default age for demo users
                "age_tier": None  # Mock users don't have age tier relationships
            },
        )
        user = mock_user
    else:
        user = User.query.get(session["user_id"])
        if not user:
            return redirect(url_for("auth.login"))

        # Get user's progress statistics
        total_words = VocabularyWord.query.filter_by(tier_id=user.tier_id).count()
        learned_words = UserProgress.query.filter(
            UserProgress.user_id == user.id, UserProgress.mastery_level >= 80
        ).count()

        progress_percentage = (learned_words / total_words * 100) if total_words > 0 else 0

    return render_template(
        "learning/dashboard.html",
        user=user,
        total_words=total_words,
        learned_words=learned_words,
        progress_percentage=round(progress_percentage, 1),
    )


@bp.route("/vocabulary")
def vocabulary():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Handle demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        tier_id = session.get("tier_id", 3)  # Default to Elementary
        tier_words_query = VocabularyWord.query.filter_by(tier_id=tier_id).limit(20).all()
    else:
        user = User.query.get(session["user_id"])
        if not user:
            return redirect(url_for("auth.login"))
        tier_words_query = VocabularyWord.query.filter_by(tier_id=user.tier_id).limit(20).all()

    # Convert to dictionaries for JSON serialization in template
    tier_words = [
        {
            "id": word.id,
            "word": word.word,
            "definition": word.definition,
            "part_of_speech": word.part_of_speech,
            "category": word.category,
            "difficulty_level": word.difficulty_level,
        }
        for word in tier_words_query
    ]

    # Create mock user object for demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        mock_user = type(
            "obj",
            (object,),
            {
                "username": session.get("username", "Guest User"),
                "tier_id": session.get("tier_id", 3),
            },
        )
        user = mock_user

    return render_template("learning/vocabulary.html", words=tier_words, user=user)


@bp.route("/practice")
def practice():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Handle demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        tier_id = session.get("tier_id", 3)  # Default to Elementary
        # For demo/guest users, just get vocabulary words for their tier
        practice_words_query = VocabularyWord.query.filter_by(tier_id=tier_id).limit(10).all()
    else:
        user = User.query.get(session["user_id"])
        if not user:
            return redirect(url_for("auth.login"))

        # Get words that need practice (low mastery or not practiced recently)
        practice_words_query = (
            db.session.query(VocabularyWord)
            .outerjoin(
                UserProgress,
                (UserProgress.vocabulary_word_id == VocabularyWord.id)
                & (UserProgress.user_id == user.id),
            )
            .filter(VocabularyWord.tier_id == user.tier_id)
            .filter(db.or_(UserProgress.mastery_level < 70, UserProgress.mastery_level.is_(None)))
            .limit(10)  # Simplified limit instead of using age_tier.words_per_session
            .all()
        )

    # Convert to dictionaries for JSON serialization
    practice_words = [
        {
            "id": word.id,
            "word": word.word,
            "definition": word.definition,
            "difficulty_level": getattr(word, "difficulty_level", 1),
        }
        for word in practice_words_query
    ]

    # Create mock user object for demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        mock_user = type(
            "obj",
            (object,),
            {
                "username": session.get("username", "Guest User"),
                "tier_id": session.get("tier_id", 3),
            },
        )
        user = mock_user

    return render_template("learning/practice.html", words=practice_words, user=user)


@bp.route("/practice/submit", methods=["POST"])
def submit_practice():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    word_id = data.get("word_id")
    is_correct = data.get("is_correct", False)

    user_id = session["user_id"]

    # Handle demo and guest users (no persistent progress)
    if session.get("is_demo") or session.get("is_guest"):
        # Return mock progress data for demo/guest users
        return jsonify(
            {
                "success": True,
                "mastery_level": 75 if is_correct else 50,
                "attempts": 3,
                "correct_answers": 2,
            }
        )

    # Find or create progress record for regular users
    progress = UserProgress.query.filter_by(user_id=user_id, vocabulary_word_id=word_id).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            vocabulary_word_id=word_id,
            attempts=0,
            correct_answers=0,
            mastery_level=0,
        )
        db.session.add(progress)

    # Update progress
    progress.attempts += 1
    if is_correct:
        progress.correct_answers += 1

    # Calculate mastery level (simple algorithm)
    if progress.attempts > 0:
        accuracy = progress.correct_answers / progress.attempts
        progress.mastery_level = min(100, int(accuracy * 100))

    progress.last_practiced = datetime.utcnow()

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "mastery_level": progress.mastery_level,
            "attempts": progress.attempts,
            "correct_answers": progress.correct_answers,
        }
    )


@bp.route("/achievements")
def achievements():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Handle demo and guest users
    if session.get("is_demo") or session.get("is_guest"):
        # Mock achievements data for demo/guest users
        total_mastered = 15
        practice_streak = 3
        mock_user = type(
            "obj",
            (object,),
            {
                "username": session.get("username", "Guest User"),
                "tier_id": session.get("tier_id", 3),
            },
        )
        user = mock_user
    else:
        user = User.query.get(session["user_id"])
        if not user:
            return redirect(url_for("auth.login"))

        # Calculate achievements data
        total_mastered = UserProgress.query.filter(
            UserProgress.user_id == user.id, UserProgress.mastery_level >= 80
        ).count()
        practice_streak = 1  # Placeholder - would need more complex logic

    # Mock achievements data structure that matches the template
    achievements = {
        "earned": [],  # No earned achievements yet
        "available": [
            {
                "icon": "🏆",
                "name": "First Achievement" if user.tier_id > 2 else "First Winner",
                "description": (
                    "Earn your first achievement by mastering 5 vocabulary words"
                    if user.tier_id > 2
                    else "Win your first prize by learning 5 words!"
                ),
                "points": 10,
                "progress": min(100, (total_mastered / 5) * 100),
            },
            {
                "icon": "🔥",
                "name": "Learning Streak" if user.tier_id > 2 else "Hot Streak",
                "description": (
                    "Maintain a 7-day learning streak"
                    if user.tier_id > 2
                    else "Practice for 3 days in a row!"
                ),
                "points": 25,
                "progress": min(100, (practice_streak / 7) * 100),
            },
            {
                "icon": "⭐",
                "name": "Vocabulary Master" if user.tier_id > 2 else "Super Star",
                "description": (
                    "Master 50 vocabulary words in your tier"
                    if user.tier_id > 2
                    else "Learn 25 words to become a super star!"
                ),
                "points": 50,
                "progress": min(100, (total_mastered / (50 if user.tier_id > 2 else 25)) * 100),
            },
        ],
    }

    # Add user stats for template
    user.total_points = 0  # Placeholder
    user.words_learned = total_mastered
    user.total_words = VocabularyWord.query.filter_by(tier_id=user.tier_id).count()
    user.practice_sessions = 1  # Placeholder
    user.streak_days = practice_streak

    # Calculate progress percentages for template (avoiding min() function in template)
    user.practice_progress = (
        min(user.practice_sessions / 50 * 100, 100) if user.practice_sessions else 0
    )
    user.streak_progress = min(user.streak_days / 30 * 100, 100) if user.streak_days else 0

    return render_template("learning/achievements.html", user=user, achievements=achievements)
