#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add src to path
sys.path.insert(0, 'src')

from src.models.user import db, User
from src.models.content import Content, DistributionLog
from src.main import app

def init_database():
    """Initialize the database with all tables"""
    print("🔄 Initializing database...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create a default user for demo purposes
        existing_user = User.query.filter_by(id=1).first()
        if not existing_user:
            demo_user = User(
                username="demo_user",
                email="demo@example.com"
            )
            demo_user.id = 1
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo user created with ID: 1")
        else:
            print("✅ Demo user already exists")
        
        print("🎉 Database initialization complete!")

if __name__ == "__main__":
    init_database()
