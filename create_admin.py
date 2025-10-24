#!/usr/bin/env python3
"""
Simple script to create an admin user for the Flask Coupon Admin Panel
Usage: python create_admin.py
"""

from app.app import app, db, User

def create_admin_user(username="admin", password="admin123"):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            return
        
        # Create new admin user
        admin = User(username=username, is_admin=True)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change this password after first login!")

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin_user()

