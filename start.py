#!/usr/bin/env python3
"""
Simple startup script for Academia Validator
This script ensures proper setup before starting the Flask application
"""

import os
import sys

def ensure_directories():
    """Ensure all required directories exist"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = ['database', 'uploads', 'static']
    
    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✓ Created directory: {dir_path}")
        else:
            print(f"✓ Directory exists: {dir_path}")

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'werkzeug',
        'PIL',
        'PyPDF2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print("pip install Flask Flask-SQLAlchemy Werkzeug Pillow PyPDF2 python-dateutil requests")
        return False
    
    return True

def main():
    print("=== Academia Validator Startup ===")
    print("Preparing to start the certificate verification system...\n")
    
    # Ensure directories exist
    print("Checking directories...")
    ensure_directories()
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\n❌ Cannot start - missing dependencies!")
        return False
    
    print("\n✅ All checks passed!")
    print("Starting Flask application...\n")
    
    # Import and run the main application
    try:
        from app import app
        print("🚀 Starting server at http://localhost:5000")
        print("📊 Admin dashboard at http://localhost:5000/admin")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)