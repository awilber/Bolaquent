import pytest
from app import create_app
from models import db, User, AgeTier, VocabularyWord

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Create test data
        tier = AgeTier(
            id=1,
            name="Test Tier", 
            min_age=5, 
            max_age=10,
            words_per_session=10
        )
        db.session.add(tier)
        
        word = VocabularyWord(
            word="test",
            definition="A trial or examination",
            tier_id=1
        )
        db.session.add(word)
        
        db.session.commit()
        
        yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

def test_index_page(client):
    """Test the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Bolaquent' in response.data

def test_login_page(client):
    """Test the login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_user_creation(app):
    """Test user creation and tier assignment."""
    with app.app_context():
        user = User(username="testuser", age=8, tier_id=1)
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.age == 8
        assert retrieved_user.tier_id == 1

def test_vocabulary_word_retrieval(app):
    """Test vocabulary word retrieval by tier."""
    with app.app_context():
        words = VocabularyWord.query.filter_by(tier_id=1).all()
        assert len(words) > 0
        assert words[0].word == "test"

def test_age_tier_functionality(app):
    """Test age tier system."""
    with app.app_context():
        tier = AgeTier.query.filter_by(name="Test Tier").first()
        assert tier is not None
        assert tier.min_age == 5
        assert tier.max_age == 10