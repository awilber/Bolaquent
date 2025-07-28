from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Text, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class AgeTier(db.Model):
    __tablename__ = 'age_tiers'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), nullable=False)
    min_age = db.Column(Integer, nullable=False)
    max_age = db.Column(Integer, nullable=False)
    description = db.Column(Text)
    cognitive_stage = db.Column(String(100))
    attention_span_minutes = db.Column(Integer)
    words_per_session = db.Column(Integer)
    
    # Relationships
    users = relationship("User", back_populates="age_tier")
    vocabulary_words = relationship("VocabularyWord", back_populates="age_tier")
    
    def __repr__(self):
        return f'<AgeTier {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    age = db.Column(Integer)
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_active = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    age_tier = relationship("AgeTier", back_populates="users")
    progress_records = relationship("UserProgress", back_populates="user")
    
    def __repr__(self):
        return f'<User {self.username}>'

class VocabularyWord(db.Model):
    __tablename__ = 'vocabulary_words'
    
    id = db.Column(Integer, primary_key=True)
    word = db.Column(String(100), nullable=False)
    definition = db.Column(Text, nullable=False)
    pronunciation = db.Column(String(200))
    part_of_speech = db.Column(String(50))
    difficulty_level = db.Column(Integer, default=1)
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    category = db.Column(String(100))  # e.g., 'animals', 'colors', 'actions'
    
    # Relationships
    age_tier = relationship("AgeTier", back_populates="vocabulary_words")
    progress_records = relationship("UserProgress", back_populates="vocabulary_word")
    
    def __repr__(self):
        return f'<VocabularyWord {self.word}>'

class GrammarRule(db.Model):
    __tablename__ = 'grammar_rules'
    
    id = db.Column(Integer, primary_key=True)
    rule_name = db.Column(String(200), nullable=False)
    explanation = db.Column(Text, nullable=False)
    examples = db.Column(Text)  # JSON string of examples
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    difficulty_level = db.Column(Integer, default=1)
    category = db.Column(String(100))  # e.g., 'verbs', 'pronouns', 'sentence_structure'
    
    def __repr__(self):
        return f'<GrammarRule {self.rule_name}>'

class LearningActivity(db.Model):
    __tablename__ = 'learning_activities'
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    activity_type = db.Column(String(50), nullable=False)  # 'matching', 'fill_blank', 'multiple_choice'
    instructions = db.Column(Text)
    content_data = db.Column(Text)  # JSON string of activity data
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    difficulty_level = db.Column(Integer, default=1)
    estimated_duration_minutes = db.Column(Integer)
    
    def __repr__(self):
        return f'<LearningActivity {self.title}>'

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    vocabulary_word_id = db.Column(Integer, ForeignKey('vocabulary_words.id'))
    activity_id = db.Column(Integer, ForeignKey('learning_activities.id'))
    
    # Progress tracking
    attempts = db.Column(Integer, default=0)
    correct_answers = db.Column(Integer, default=0)
    mastery_level = db.Column(Integer, default=0)  # 0-100 scale
    last_practiced = db.Column(DateTime, default=datetime.utcnow)
    next_review_date = db.Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    vocabulary_word = relationship("VocabularyWord", back_populates="progress_records")
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Word:{self.vocabulary_word_id}>'

class GamificationElement(db.Model):
    __tablename__ = 'gamification_elements'
    
    id = db.Column(Integer, primary_key=True)
    element_type = db.Column(String(50), nullable=False)  # 'badge', 'achievement', 'level'
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    unlock_criteria = db.Column(Text)  # JSON string of criteria
    icon_path = db.Column(String(200))
    points_value = db.Column(Integer, default=0)
    
    def __repr__(self):
        return f'<GamificationElement {self.name}>'