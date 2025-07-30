from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, VocabularyWord, GrammarRule, AgeTier, User
import subprocess
import sys

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
def dashboard():
    # Simple admin dashboard
    total_users = User.query.count()

    stats = {
        "total_users": total_users,
        "total_words": VocabularyWord.query.count(),
        "active_sessions": 1,  # Placeholder
        "total_practice_sessions": 10,  # Placeholder
        "tier_distribution": [],
    }

    # Get user distribution by tier
    for tier in AgeTier.query.all():
        user_count = User.query.filter_by(tier_id=tier.id).count()
        stats["tier_distribution"].append(
            {
                "name": tier.name,
                "age_range": f"{tier.min_age}-{tier.max_age}",
                "user_count": user_count,
            }
        )

    return render_template("admin/dashboard.html", stats=stats)


@bp.route("/words")
def manage_words():
    words = VocabularyWord.query.all()
    tiers = AgeTier.query.all()
    return render_template("admin/words.html", words=words, tiers=tiers)


@bp.route("/words/add", methods=["POST"])
def add_word():
    word = request.form.get("word")
    definition = request.form.get("definition")
    tier_id = request.form.get("tier_id", type=int)
    part_of_speech = request.form.get("part_of_speech")
    category = request.form.get("category")
    difficulty = request.form.get("difficulty_level", type=int, default=1)

    if word and definition and tier_id:
        new_word = VocabularyWord(
            word=word,
            definition=definition,
            tier_id=tier_id,
            part_of_speech=part_of_speech,
            category=category,
            difficulty_level=difficulty,
        )

        db.session.add(new_word)
        db.session.commit()
        flash(f'Word "{word}" added successfully!')
    else:
        flash("Please fill in all required fields")

    return redirect(url_for("admin.manage_words"))


@bp.route("/tiers")
def manage_tiers():
    tiers = AgeTier.query.all()
    return render_template("admin/tiers.html", tiers=tiers)


@bp.route("/users")
def manage_users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@bp.route("/expand-vocabulary", methods=["POST"])
def expand_vocabulary():
    """Expand vocabulary by 100x for all tiers"""
    try:
        # Run vocabulary expansion script
        from expand_vocabulary import expand_vocabulary_by_tier
        expand_vocabulary_by_tier()
        
        # Get updated stats
        total_words = VocabularyWord.query.count()
        flash(f"Vocabulary successfully expanded! Total words: {total_words}")
        
    except Exception as e:
        flash(f"Error expanding vocabulary: {str(e)}")
    
    return redirect(url_for("admin.dashboard"))
