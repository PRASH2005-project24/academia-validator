#!/usr/bin/env python3
"""
Database initialization script for Academia Validator
This script creates all database tables and adds sample data
"""

import os
import sys
from datetime import datetime, date

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize the database with tables and sample data"""
    try:
        from flask import Flask
        from backend.models import db, Institution, Certificate, VerificationLog, Admin
        
        # Create Flask app with same config as main app
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'your-secret-key-here'
        
        # Use absolute path for database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'academia_validator.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Ensure database directory exists
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
        os.makedirs(db_dir, exist_ok=True)
        print(f"✓ Database directory: {db_dir}")
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            print("Creating database tables...")
            
            # Drop all tables first (fresh start)
            db.drop_all()
            print("✓ Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("✓ Created all tables")
            
            # Add sample institutions
            if Institution.query.count() == 0:
                print("Adding sample institutions...")
                sample_institutions = [
                    Institution(name="Ranchi University", code="RU", state="Jharkhand", established_year=1960),
                    Institution(name="Birla Institute of Technology", code="BIT", state="Jharkhand", established_year=1955),
                    Institution(name="NIT Jamshedpur", code="NIT_JSR", state="Jharkhand", established_year=1960)
                ]
                
                for inst in sample_institutions:
                    db.session.add(inst)
                
                db.session.commit()
                print("✓ Added sample institutions")
            
            # Add sample certificates
            if Certificate.query.count() == 0:
                print("Adding sample certificates...")
                sample_certificates = [
                    Certificate(
                        certificate_number="RU2023001",
                        student_name="John Doe",
                        roll_number="2019CS001",
                        course_name="B.Tech Computer Science",
                        degree_type="Bachelor",
                        graduation_year=2023,
                        cgpa_percentage="8.5",
                        issue_date=date(2023, 6, 15),
                        institution_id=1
                    ),
                    Certificate(
                        certificate_number="BIT2022045",
                        student_name="Jane Smith",
                        roll_number="2018EC045",
                        course_name="B.Tech Electronics",
                        degree_type="Bachelor",
                        graduation_year=2022,
                        cgpa_percentage="9.2",
                        issue_date=date(2022, 5, 20),
                        institution_id=2
                    ),
                    Certificate(
                        certificate_number="NIT_JSR2024030",
                        student_name="Alice Johnson",
                        roll_number="2020ME030",
                        course_name="B.Tech Mechanical Engineering",
                        degree_type="Bachelor",
                        graduation_year=2024,
                        cgpa_percentage="8.8",
                        issue_date=date(2024, 7, 10),
                        institution_id=3
                    )
                ]
                
                for cert in sample_certificates:
                    cert.certificate_hash = cert.generate_hash()
                    db.session.add(cert)
                
                db.session.commit()
                print("✓ Added sample certificates")
            
            # Add a sample verification log
            if VerificationLog.query.count() == 0:
                print("Adding sample verification log...")
                sample_log = VerificationLog(
                    certificate_number="RU2023001",
                    student_name="John Doe",
                    institution_name="Ranchi University",
                    verification_result="Valid",
                    confidence_score=95.5,
                    extracted_text="Sample extracted text",
                    verified_by="127.0.0.1",
                    uploaded_filename="sample_certificate.pdf",
                    file_hash="abc123def456"
                )
                db.session.add(sample_log)
                db.session.commit()
                print("✓ Added sample verification log")
            
            print(f"\n✅ Database initialized successfully!")
            print(f"Database location: {db_path}")
            
            # Print summary
            inst_count = Institution.query.count()
            cert_count = Certificate.query.count()
            log_count = VerificationLog.query.count()
            
            print(f"\nDatabase Summary:")
            print(f"- Institutions: {inst_count}")
            print(f"- Certificates: {cert_count}")
            print(f"- Verification Logs: {log_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Academia Validator Database Initialization ===")
    print("Initializing database with tables and sample data...\n")
    
    success = init_database()
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now start the application with:")
        print("  python app.py")
        print("  or")
        print("  python start.py")
    else:
        print("\n❌ Database initialization failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)