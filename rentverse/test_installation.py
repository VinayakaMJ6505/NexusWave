#!/usr/bin/env python3
"""
Test script to verify RentAssured installation
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_bcrypt',
        'flask_jwt_extended',
        'pymysql',
        'mysql.connector'
    ]
    
    print("🔍 Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_database_connection():
    """Test database connection"""
    try:
        from app import app, db
        
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    try:
        from app import app
        print("✅ Flask application created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask application creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 RentAssured Installation Test")
    print("=" * 50)
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is too old. Required: 3.8+")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Some required modules are missing. Run: pip install -r requirements.txt")
        return False
    
    # Test Flask app
    if not test_flask_app():
        print("\n❌ Flask application test failed")
        return False
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed")
        print("💡 Make sure MySQL is running and database 'rentassured' exists")
        print("💡 Run: python setup_database.py")
        return False
    
    print("\n🎉 All tests passed! RentAssured is ready to run.")
    print("\nNext steps:")
    print("1. Run: python run.py")
    print("2. Open: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
