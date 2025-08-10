# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Response Header Requirement

All responses from Claude Code must begin with a header in the following format (with labels in white/light gray):

```
<span style="color: #f0f0f0">Project:</span>
Bolaquent
<span style="color: #f0f0f0">Path:</span>
/Users/arlonwilber/Library/CloudStorage/GoogleDrive-awilber@wiredtriangle.com/Shared drives/AW/Personal/Projects/Bolaquent
<span style="color: #f0f0f0">Date/Time:</span>
[Current date and time]
<span style="color: #f0f0f0">Launch:</span>
cd "/Users/arlonwilber/Library/CloudStorage/GoogleDrive-awilber@wiredtriangle.com/Shared drives/AW/Personal/Projects/Bolaquent" && source venv/bin/activate && python app.py
---
```

## Project Overview

Bolaquent is a multi-tiered vocabulary and grammar learning app designed for learners from early verbal stages (age 2) to highly educated adults. The app features age-appropriate gamification and adaptive difficulty scaling based on cognitive development research.

**Target Audience**: English language learners (designed for future multi-language support)
**Age Tiers**: 6 pedagogically-based learning tiers (Early Verbal, Preschool, Elementary, Middle School, High School, Adult)
**Platform**: Cross-platform Flask web app with responsive design

## Common Development Commands

### Environment Setup & Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (if needed)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Running the Application
```bash
# Start development server (preferred)
python app.py

# Alternative Flask command
export FLASK_APP=app.py
flask run

# Run with specific port
PORT=5020 python app.py
```

### Database Operations
```bash
# Initialize database with sample data
python -c "from app import create_app; app = create_app(); app.test_request_context().push(); exec(open('init_db.py').read())"

# Or use the built-in init route
curl http://localhost:5000/init-db
```

### Code Quality & Testing
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# Format code
black --line-length=100 .

# Lint code  
flake8 . --max-line-length=100 --ignore=E203,W503

# Type checking
mypy . --ignore-missing-imports
```

### Git Flow Commands
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Release to production (triggers deployment)
git checkout main
git merge develop
git push origin main
```

## Architecture & Code Structure

### Core Application Pattern
- **Flask Application Factory**: `create_app()` in `app.py` initializes the application
- **Blueprint Architecture**: Modular routing with separate blueprints for auth, learning, and admin
- **SQLAlchemy ORM**: Database models in `models.py` with relationship mapping
- **Configuration Management**: Environment-based config in `config.py`

### Key Components

#### Database Models (`models.py`)
- **AgeTier**: 6 cognitive development-based learning tiers
- **User**: User accounts with age-based tier assignment
- **VocabularyWord**: Tier-specific vocabulary content
- **UserProgress**: Individual learning progress tracking
- **GrammarRule & LearningActivity**: Content framework (expandable)

#### Blueprint Structure (`routes/`)
- **auth.py**: User authentication and tier assignment
- **learning.py**: Learning dashboard and vocabulary practice
- **admin.py**: Content management and analytics

#### Age Tier System
The core pedagogical framework with 6 tiers:
1. **Early Verbal (2-4)**: Sensory learning, 5 words/session, 5-minute attention span
2. **Preschool (4-6)**: Language explosion, 8 words/session, 10-minute attention span
3. **Elementary (6-10)**: Concrete operational, 12 words/session, 15-minute attention span
4. **Middle School (11-14)**: Abstract thinking, 15 words/session, 25-minute attention span
5. **High School (15-18)**: Advanced reasoning, 20 words/session, 30-minute attention span
6. **Adult (18+)**: Self-directed learning, 25 words/session, 45-minute attention span

### Database Initialization
The application auto-creates tables and sample data on first run. The `init_db()` route populates:
- All 6 age tiers with cognitive development parameters
- Sample vocabulary words distributed across tiers
- Proper tier relationships and constraints

### Port Management Protocol
The application MUST use the centralized port management system:
- Register with port-manager: `../utils/port-manager`
- Kill only Bolaquent processes: `ps aux | grep -E "(app.py|Bolaquent)" | grep -v grep | awk '{print $2}' | xargs kill -9`
- Use allocated port: Check existing allocation with `node index.js --app-name "Bolaquent" --check-existing`
- Start with allocated port: `PORT=ALLOCATED_PORT python app.py`
- Register PID after startup: `node index.js --app-name "Bolaquent" --register-ports PORT --pid $PID`

## Infrastructure

**Repository**: https://github.com/awilber/Bolaquent
**AWS Instance**: i-0332d1b2863b08d95  
**Public IP**: 54.89.117.172
**Security Group**: sg-027bbdda70b9ae03b
**Local Development**: http://localhost:5000 (or next available port)
**Production**: http://54.89.117.172:5000

## Comprehensive QA Protocol

### Mandatory Testing Before Completion
Before marking any task as complete, run comprehensive testing:
```bash
# 1. Service Verification
ps aux | grep app.py | grep -v grep  # Verify process running
curl -I http://localhost:PORT/        # Verify HTTP response

# 2. Authentication Flow Testing
curl -X POST -d "username=testuser11&age=11" -c cookies.txt http://localhost:PORT/auth/login

# 3. All Page Verification
curl -b cookies.txt -s http://localhost:PORT/learning/dashboard | grep -E "(<title>|error)" | head -1
curl -b cookies.txt -s http://localhost:PORT/learning/vocabulary | grep -E "(<title>|error)" | head -1
curl -b cookies.txt -s http://localhost:PORT/learning/practice | grep -E "(<title>|error)" | head -1
curl -b cookies.txt -s http://localhost:PORT/learning/achievements | grep -E "(<title>|error)" | head -1
curl -b cookies.txt -s http://localhost:PORT/admin/ | grep -E "(<title>|error)" | head -1
```

### QA Completion Criteria
✅ All 5 core pages return proper HTML titles (not errors)
✅ Authentication flow works correctly
✅ Service responds to HTTP requests
✅ No Python exceptions in terminal output
✅ Database queries execute without errors

### AWS Deployment Verification
After any deployment claims:
```bash
curl -I http://54.89.117.172/ 2>&1 | head -5
# Must show successful connection, not "Connection refused"
```

## Development Workflow

### Git Flow Methodology
- **main**: Production-ready code, triggers AWS deployment
- **develop**: Integration branch for features
- **feature/***: Feature development branches
- **CI/CD Pipeline**: Automated testing, building, and deployment on push to main

### Testing Strategy
- **Unit Tests**: `test_app.py` with pytest fixtures
- **Test Coverage**: HTML coverage reports in `htmlcov/`
- **CI Pipeline**: Multi-version Python testing (3.9, 3.10, 3.11)

### Deployment
```bash
# Deploy to AWS (from main branch)
./deployment/aws-setup.sh

# SSH access
ssh -i ~/.ssh/customer-success-key-east.pem ec2-user@54.89.117.172
```