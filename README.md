# 🎓 Bolaquent - Multi-Tiered Vocabulary Learning

[![CI/CD Pipeline](https://github.com/awilber/Bolaquent/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/awilber/Bolaquent/actions/workflows/ci-cd.yml)

A comprehensive vocabulary and grammar learning application designed for learners from early verbal stages (age 2) to highly educated adults, featuring age-appropriate gamification and adaptive difficulty scaling.

## 🌟 Features

- **📚 Pedagogically-Based Age Tiers**: 6 learning tiers based on cognitive development research
- **🎮 Adaptive Gamification**: Age-appropriate engagement mechanics for each tier
- **📈 Progress Tracking**: Individual learning progress with mastery levels
- **⚙️ Admin Interface**: Content management and user analytics
- **🌍 Multi-Platform**: Responsive web application accessible across all devices

## 🎯 Age Tiers

| Tier | Age Range | Cognitive Stage | Focus |
|------|-----------|----------------|-------|
| 1 | 2-4 years | Early Preoperational | Sensory learning, simple words |
| 2 | 4-6 years | Advanced Preoperational | Language explosion, social play |
| 3 | 6-10 years | Concrete Operational | Logical thinking, academic vocabulary |
| 4 | 11-14 years | Emerging Formal | Abstract thinking, complex grammar |
| 5 | 15-18 years | Formal Operational | Advanced reasoning, test preparation |
| 6 | 18+ years | Postformal | Self-directed, specialized domains |

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/awilber/Bolaquent.git
cd Bolaquent

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"

# Run application
python3 app.py
```

**Local URL**: http://localhost:5020

### Live Application

**Production URL**: http://54.89.117.172:5000

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Jinja2 templates with responsive CSS
- **Deployment**: AWS EC2 with automated CI/CD

### Project Structure
```
Bolaquent/
├── app.py              # Flask application factory
├── models.py           # Database models
├── config.py           # Configuration management
├── routes/             # Blueprint modules
│   ├── auth.py         # Authentication routes
│   ├── learning.py     # Learning activities
│   └── admin.py        # Admin interface
├── templates/          # Jinja2 templates
├── docs/              # Documentation
└── deployment/        # AWS deployment scripts
```

## 🔄 Git Flow Methodology

This project follows Git Flow branching strategy:

- **main**: Production-ready code, triggers AWS deployment
- **develop**: Integration branch for features
- **feature/***: Feature development branches
- **release/***: Release preparation branches
- **hotfix/***: Critical production fixes

### Development Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Work on feature...
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Create PR to develop branch
# After review and merge, feature is integrated

# Release to production
git checkout main
git pull origin main
git merge develop
git push origin main  # Triggers automated deployment
```

## 🚀 CI/CD Pipeline

Automated pipeline runs on every push and pull request:

### 🧪 Test Stage
- Multi-version Python testing (3.9, 3.10, 3.11)
- Code linting with flake8
- Code formatting with black
- Type checking with mypy
- Unit tests with pytest

### 📦 Build Stage
- Creates deployment package
- Installs dependencies
- Generates deployment artifact

### 🌐 Deploy Stage (main branch only)
- Uploads to S3 for backup
- Deploys to EC2 via AWS SSM
- Verifies deployment health
- Sends deployment notifications

## 🛠️ Development

### Running Tests
```bash
pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Formatting
black --line-length=100 .

# Linting  
flake8 . --max-line-length=100

# Type checking
mypy . --ignore-missing-imports
```

### Database Management
```bash
# Initialize database with sample data
python3 -c "from app import create_app; app = create_app(); app.test_request_context().push(); exec(open('init_db.py').read())"
```

## 📊 Admin Interface

Access the admin panel at `/admin` to:
- Manage vocabulary words by tier
- View user progress analytics
- Add new learning content
- Monitor system usage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request to `develop` branch

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/awilber/Bolaquent/issues)
- **Documentation**: [Project Wiki](https://github.com/awilber/Bolaquent/wiki)
- **Live Demo**: http://54.89.117.172:5000# Repository successfully cleaned and ready for Smart Port Management CI/CD
# Force re-deploy with hero backgrounds
# Force redeploy - Mon Aug 11 12:18:53 EDT 2025
