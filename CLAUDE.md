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
python app.py
---
```

## Project Overview

Bolaquent is a multi-tiered vocabulary and grammar learning app designed for learners from early verbal stages to highly educated adults. The app features age-appropriate gamification and adaptive difficulty scaling.

**Target Audience**: English language learners (designed for future multi-language support)
**Age Tiers**: Based on pedagogical best practices for cognitive development
**Platform**: Cross-platform Flask web app with responsive design

## Infrastructure

**Repository**: https://github.com/awilber/Bolaquent
**AWS Instance**: i-0332d1b2863b08d95  
**Public IP**: 54.89.117.172
**Security Group**: sg-027bbdda70b9ae03b

## Development Setup

```bash
# Clone repository
git clone https://github.com/awilber/Bolaquent.git
cd Bolaquent

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run locally
python app.py
```

## Deployment

```bash
# Deploy to AWS
./deploy.sh

# SSH to instance
ssh -i ~/.ssh/customer-success-key-east.pem ec2-user@54.89.117.172
```

## Architecture Pattern

Following the established Flask blueprint pattern from other projects:
- Flask app with modular blueprints
- SQLAlchemy for database management
- Blueprint-based routing for different learning modules
- Cross-platform responsive design
- Age-tier based content delivery system