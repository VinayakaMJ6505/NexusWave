#!/usr/bin/env python3
"""
RentAssured Application Runner
This script starts the Flask application with proper configuration
"""

import os
import sys
from app import app, db

def check_database_connection():
    """Check if database connection is working"""
    try:
        with app.app_context():
            db.engine.execute('SELECT 1')
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please make sure:")
        print("1. MySQL server is running")
        print("2. Database 'rentassured' exists")
        print("3. Database credentials are correct in app.py")
        return False

def create_tables():
    """Create database tables if they don't exist"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def main():
    """Main function to start the application"""
    print("🚀 Starting RentAssured Application...")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("\n💡 To set up the database, run: python setup_database.py")
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    print("✅ Application ready!")
    print("\n🌐 Starting Flask development server...")
    print("📍 Application URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

if __name__ == "__main__":
    main()
