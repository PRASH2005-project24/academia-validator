#!/usr/bin/env python3
"""
Main entry point for Academia Validator on Railway
"""

import os
from app_fixed import app
from backend.models import db

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
    # Get port from environment variable (Railway will set this)
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🚀 Starting Academia Validator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)