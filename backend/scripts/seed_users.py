#!/usr/bin/env python3
"""
Seed script to create test users (admin, driver, user) for Pi-live.
Run from backend directory after migrations:
  cd pi-live-core/backend && PYTHONPATH=src python scripts/seed_users.py
"""
import os
import sys

# Add src to path so we can import from core, common, auth
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import bcrypt
from core.db import SessionLocal
from common.models import User


def hash_password(password: str) -> str:
    """Hash password with bcrypt (compatible with passlib verify)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

TEST_USERS = [
    {"email": "admin@pilive.com", "password": "admin123", "role": "admin"},
    {"email": "dispatcher@pilive.com", "password": "dispatcher123", "role": "dispatcher"},
    {"email": "driver1@pilive.com", "password": "driver123", "role": "driver"},
    {"email": "driver2@pilive.com", "password": "driver123", "role": "driver"},
    {"email": "user1@pilive.com", "password": "user123", "role": "user"},
]


def seed_users():
    db = SessionLocal()
    try:
        for u in TEST_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"  Skip (exists): {u['email']}")
                continue
            hashed = hash_password(u["password"])
            user = User(
                email=u["email"],
                password=hashed,
                roles=[u["role"]],
                is_otp_verified=True,
            )
            db.add(user)
            print(f"  Created: {u['email']} ({u['role']})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding test users...")
    seed_users()
    print("\n" + "=" * 50)
    print("Test accounts (use these to login at http://localhost:3000):")
    print("=" * 50)
    print("\nAdmin:")
    print("  Email:    admin@pilive.com")
    print("  Password: admin123")
    print("\nDispatcher:")
    print("  Email:    dispatcher@pilive.com")
    print("  Password: dispatcher123")
    print("\nDrivers:")
    print("  Email:    driver1@pilive.com  |  Password: driver123")
    print("  Email:    driver2@pilive.com  |  Password: driver123")
    print("\nUser:")
    print("  Email:    user1@pilive.com")
    print("  Password: user123")
    print("=" * 50)
