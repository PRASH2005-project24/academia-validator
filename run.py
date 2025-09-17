#!/usr/bin/env python3
"""
Simple run script for Academia Validator
This is the easiest way to start your certificate verification system
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Academia Validator...")
    print("Certificate Verification System for Government of Jharkhand")
    print("-" * 60)
    
    # Check if database exists
    db_path = "database/academia_validator.db"
    if not os.path.exists(db_path):
        print("⚠️  Database not found. Initializing...")
        try:
            subprocess.run([sys.executable, "init_db.py"], check=True)
            print("✅ Database initialized successfully!")
        except subprocess.CalledProcessError:
            print("❌ Database initialization failed. Please run 'python init_db.py' manually.")
            return False
    
    print("\n🌐 Starting web server...")
    print("📍 Open your browser to:")
    print("   🏠 Main Interface: http://localhost:8080")
    print("   👤 Admin Dashboard: http://localhost:8080/admin")
    print("   🧪 Test Page: http://localhost:8080/test")
    print("\n✨ Features available:")
    print("   • Certificate verification (drag & drop upload)")
    print("   • Institution management") 
    print("   • Verification statistics")
    print("   • Sample data included")
    print("\n" + "=" * 60)
    print("🎓 Academia Validator is starting...")
    print("=" * 60)
    
    # Run the fixed application
    try:
        subprocess.run([sys.executable, "app_fixed.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using Academia Validator!")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)