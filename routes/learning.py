from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models import db, User, VocabularyWord, UserProgress, AgeTier
from datetime import datetime

bp = Blueprint("learning", __name__, url_prefix="/learning")


@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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

    user = User.query.get(session["user_id"])
    tier_words = VocabularyWord.query.filter_by(tier_id=user.tier_id).limit(20).all()

    return render_template("learning/vocabulary.html", words=tier_words, user=user)


@bp.route("/practice")
def practice():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    # Get words that need practice (low mastery or not practiced recently)
    practice_words = (
        db.session.query(VocabularyWord)
        .outerjoin(
            UserProgress,
            (UserProgress.vocabulary_word_id == VocabularyWord.id)
            & (UserProgress.user_id == user.id),
        )
        .filter(VocabularyWord.tier_id == user.tier_id)
        .filter(db.or_(UserProgress.mastery_level < 70, UserProgress.mastery_level.is_(None)))
        .limit(user.age_tier.words_per_session)
        .all()
    )

    return render_template("learning/practice.html", words=practice_words, user=user)


@bp.route("/practice/submit", methods=["POST"])
def submit_practice():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    word_id = data.get("word_id")
    is_correct = data.get("is_correct", False)

    user_id = session["user_id"]

    # Find or create progress record
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

    user = User.query.get(session["user_id"])

    # Calculate achievements
    total_mastered = UserProgress.query.filter(
        UserProgress.user_id == user.id, UserProgress.mastery_level >= 80
    ).count()

    practice_streak = 1  # Placeholder - would need more complex logic

    achievements = {
        "words_mastered": total_mastered,
        "practice_streak": practice_streak,
        "tier_name": user.age_tier.name if user.age_tier else "Unknown",
    }

    return render_template("learning/achievements.html", user=user, achievements=achievements)
