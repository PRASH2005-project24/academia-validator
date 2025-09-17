#!/usr/bin/env python3
"""
Main entry point for Academia Validator on Render
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app_fixed import app
    from backend.models import db
    print("✅ Successfully imported app and models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

if __name__ == '__main__':
    try:
        # Initialize database tables
        with app.app_context():
            # Ensure database directory exists
            db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
            os.makedirs(db_dir, exist_ok=True)
            
            db.create_all()
            print("✅ Database tables created successfully!")
        
        # Get port from environment variable (Render will set this)
        port = int(os.environ.get('PORT', 10000))
        
        print(f"🚀 Starting Academia Validator on port {port}")
        print(f"📍 Server will be available at: 0.0.0.0:{port}")
        
        # Use gunicorn-like settings for better production performance
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)
