# Bolaquent Developer Guide

## Architecture Overview

### Technology Stack
- **Backend:** Flask 3.1.0 with SQLAlchemy ORM
- **Database:** SQLite (development) / PostgreSQL (production ready)
- **Frontend:** Jinja2 templates with responsive CSS
- **Testing:** pytest with coverage reporting
- **CI/CD:** GitHub Actions with AWS deployment
- **Code Quality:** black, flake8, mypy for consistent code style

### Project Structure
```
Bolaquent/
├── app.py              # Flask application factory
├── config.py           # Application configuration
├── models.py           # SQLAlchemy database models
├── requirements.txt    # Python dependencies
├── routes/             # Blueprint modules
│   ├── __init__.py
│   ├── auth.py         # Authentication routes
│   ├── learning.py     # Learning activities
│   └── admin.py        # Admin interface
├── templates/          # Jinja2 templates
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── auth/           # Authentication templates
│   ├── learning/       # Learning interface templates
│   └── admin/          # Admin panel templates
├── static/             # CSS, JavaScript, images
├── docs/               # Documentation
├── deployment/         # AWS deployment scripts
├── .github/workflows/  # CI/CD pipeline
└── tests/              # Test files
```

## Database Schema

### Core Models

#### AgeTier
Defines the six learning tiers with cognitive characteristics.
```python
class AgeTier(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), nullable=False)
    min_age = db.Column(Integer, nullable=False)
    max_age = db.Column(Integer, nullable=False)
    description = db.Column(Text)
    cognitive_stage = db.Column(String(100))
    attention_span_minutes = db.Column(Integer)
    words_per_session = db.Column(Integer)
```

#### User
Stores user accounts with tier assignment.
```python
class User(db.Model):
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    age = db.Column(Integer)
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_active = db.Column(DateTime, default=datetime.utcnow)
```

#### VocabularyWord
Contains the vocabulary database with tier assignments.
```python
class VocabularyWord(db.Model):
    id = db.Column(Integer, primary_key=True)
    word = db.Column(String(100), nullable=False)
    definition = db.Column(Text, nullable=False)
    pronunciation = db.Column(String(200))
    part_of_speech = db.Column(String(50))
    difficulty_level = db.Column(Integer, default=1)
    tier_id = db.Column(Integer, ForeignKey('age_tiers.id'))
    category = db.Column(String(100))
```

#### UserProgress
Tracks individual learning progress and mastery.
```python
class UserProgress(db.Model):
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    vocabulary_word_id = db.Column(Integer, ForeignKey('vocabulary_words.id'))
    attempts = db.Column(Integer, default=0)
    correct_answers = db.Column(Integer, default=0)
    mastery_level = db.Column(Integer, default=0)  # 0-100 scale
    last_practiced = db.Column(DateTime, default=datetime.utcnow)
    next_review_date = db.Column(DateTime)
```

## Blueprint Architecture

### Authentication Blueprint (`routes/auth.py`)
- **POST /auth/login**: Simple username + age login
- **POST /auth/register**: Account creation with automatic tier assignment
- **GET /auth/logout**: Session cleanup

### Learning Blueprint (`routes/learning.py`)
- **GET /learning/dashboard**: User progress overview
- **GET /learning/vocabulary**: Browse tier-appropriate words
- **GET /learning/practice**: Interactive practice session
- **POST /learning/practice/submit**: Progress tracking endpoint
- **GET /learning/achievements**: Gamification and rewards

### Admin Blueprint (`routes/admin.py`)
- **GET /admin**: Dashboard with user statistics
- **GET /admin/words**: Vocabulary management interface
- **POST /admin/words/add**: Add new vocabulary words
- **GET /admin/tiers**: Age tier management
- **GET /admin/users**: User account management

## Configuration Management

### Environment Variables
```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bolaquent.db'
    
    # Age tier settings
    DEFAULT_TIER = 3  # Elementary as default
    WORDS_PER_SESSION = {1: 5, 2: 8, 3: 12, 4: 15, 5: 20, 6: 25}
    SESSION_TIMEOUT_MINUTES = {1: 5, 2: 10, 3: 15, 4: 25, 5: 30, 6: 45}
```

## Development Workflow

### Local Development Setup
```bash
# Clone and setup
git clone https://github.com/awilber/Bolaquent.git
cd Bolaquent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"

# Run application
python3 app.py
```

### Code Quality Standards
```bash
# Format code
black . --line-length 100

# Lint code
flake8 . --max-line-length 100 --exclude=venv

# Type checking
mypy . --ignore-missing-imports

# Run tests
pytest --cov=. --cov-report=html
```

### Git Flow Process
1. **Feature Development:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "Add new feature"
   git push origin feature/new-feature
   # Create PR to develop
   ```

2. **Release to Production:**
   ```bash
   git checkout main
   git merge develop
   git push origin main  # Triggers automated deployment
   ```

## Testing Strategy

### Unit Tests
- Model validation and relationships
- Route functionality and authentication
- Business logic and calculations
- Error handling and edge cases

### Integration Tests
- Full application workflows
- Database operations
- Template rendering
- API endpoint responses

### Test Structure
```python
# test_app.py
@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

def test_user_creation(app):
    """Test user creation and tier assignment."""
    # Test implementation
```

## Deployment Guide

### AWS Infrastructure
- **EC2 Instance:** t3.micro for application hosting
- **S3 Bucket:** Deployment artifact storage
- **Security Groups:** HTTP/HTTPS access configuration
- **IAM Roles:** Deployment permissions

### CI/CD Pipeline
The GitHub Actions workflow automatically:
1. **Test Stage:** Multi-Python version testing
2. **Build Stage:** Deployment package creation
3. **Deploy Stage:** AWS EC2 deployment via SSM
4. **Notify Stage:** Deployment status reporting

### Manual Deployment
```bash
# SSH to EC2 instance
ssh -i ~/.ssh/customer-success-key-east.pem ec2-user@54.89.117.172

# Setup application
sudo yum update -y
sudo yum install -y python3 python3-pip
git clone https://github.com/awilber/Bolaquent.git
cd Bolaquent
pip3 install --user -r requirements.txt
python3 app.py
```

## Performance Considerations

### Database Optimization
- Indexed foreign keys for fast lookups
- Efficient query patterns for progress tracking
- Connection pooling for concurrent users

### Caching Strategy
- Template caching for static content
- Database query result caching
- CDN integration for static assets

### Scalability Planning
- Horizontal scaling with load balancers
- Database sharding by user tier
- Microservice architecture migration path

## Security Implementation

### Authentication
- Session-based authentication (no passwords currently)
- CSRF protection on forms
- Secure session cookie configuration

### Data Protection
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection in templates

### Infrastructure Security
- AWS security groups with minimal access
- HTTPS enforcement in production
- Environment variable protection

## Monitoring and Logging

### Application Monitoring
- Error tracking and reporting
- Performance metrics collection
- User activity analytics

### Health Checks
- Database connection monitoring
- Application responsiveness checks
- External dependency status

## Contributing Guidelines

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Pull Request Process
1. Create feature branch from develop
2. Implement changes with tests
3. Update documentation as needed
4. Submit PR with detailed description
5. Address code review feedback
6. Merge after approval and CI success

### Issue Reporting
- Use GitHub issue templates
- Provide reproduction steps
- Include environment details
- Tag with appropriate labels