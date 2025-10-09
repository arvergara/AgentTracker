#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Initialize database
python << PYTHON
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created successfully")
PYTHON
