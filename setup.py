#!/usr/bin/env python3
"""
Setup script for GYM SUPPLEMENTS AND NUTRITION PRODUCT website
This script helps set up the application environment and dependencies.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please use Python 3.8 or higher")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating necessary directories...")
    
    directories = [
        "instance",
        "static/images/accessories/bottles",
        "static/images/accessories/bag", 
        "static/images/accessories/shoes",
        "static/images/accessories/heartratemonitor",
        "static/images/accessories/wristband",
        "static/images/accessories/headband",
        "static/images/accessories/tshirt",
        "static/images/accessories/caps",
        "static/images/accessories/tracks",
        "static/images/accessories/shorts"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created {directory}")
        except Exception as e:
            print(f"✗ Failed to create {directory}: {e}")
            return False
    
    return True

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    
    try:
        # Import and initialize the database
        from app import app, db, create_sample_data
        
        with app.app_context():
            db.create_all()
            success = create_sample_data()
            
        if success:
            print("✓ Database initialized successfully")
            return True
        else:
            print("✗ Failed to initialize database")
            return False
            
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("Running basic tests...")
    
    try:
        import test_app
        # Run file structure and syntax tests only (not the server test)
        file_test = test_app.test_file_structure()
        syntax_test = test_app.test_python_syntax()
        
        if file_test and syntax_test:
            print("✓ Basic tests passed")
            return True
        else:
            print("✗ Some tests failed")
            return False
            
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("GYM SUPPLEMENTS AND NUTRITION PRODUCT - Setup Script")
    print("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Initializing database", initialize_database),
        ("Running tests", run_tests)
    ]
    
    all_success = True
    
    for step_name, step_func in steps:
        print(f"\n{step_name}:")
        print("-" * 30)
        
        success = step_func()
        if not success:
            all_success = False
            print(f"\n❌ Setup failed at: {step_name}")
            break
    
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("\nTo start the application:")
        print("1. Run: python app.py")
        print("2. Open your browser to: http://127.0.0.1:5000")
        print("\nDefault login credentials:")
        print("Username: test")
        print("Password: password123")
    else:
        print("❌ Setup failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
