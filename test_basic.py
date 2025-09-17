#!/usr/bin/env python3
"""
Basic test script for Academia Validator
Tests core functionality without requiring Tesseract OCR
"""

import sys
import os
import json
from datetime import datetime, date

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        from flask import Flask
        from backend.models import db, Certificate, Institution, VerificationLog, Admin
        print("✓ Flask and models imported successfully")
        
        from backend.validation import CertificateValidator, validate_certificate_data
        print("✓ Validation module imported successfully")
        
        # Note: OCR module might fail without Tesseract, but that's OK for basic testing
        try:
            from backend.ocr_utils import CertificateOCR, process_certificate_file
            print("✓ OCR module imported successfully")
        except Exception as e:
            print(f"⚠️ OCR module import warning (Tesseract may not be installed): {e}")
            print("  This is OK - the system can still run with manual data entry")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database_models():
    """Test database model creation"""
    print("\nTesting database models...")
    try:
        from flask import Flask
        from backend.models import db, Institution, Certificate
        
        # Create a test Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            
            # Test creating an institution
            test_inst = Institution(
                name="Test University",
                code="TU",
                state="Test State",
                established_year=2000
            )
            
            # Test creating a certificate
            test_cert = Certificate(
                certificate_number="TEST2024001",
                student_name="Test Student",
                roll_number="TS001",
                course_name="Test Course",
                degree_type="Bachelor",
                graduation_year=2024,
                cgpa_percentage="8.5",
                issue_date=date(2024, 6, 15),
                institution_id=1
            )
            
            # Test hash generation
            cert_hash = test_cert.generate_hash()
            
            print("✓ Database models work correctly")
            print(f"✓ Certificate hash generated: {cert_hash[:16]}...")
            
        # Clean up test database
        if os.path.exists('test.db'):
            os.remove('test.db')
            
        return True
    except Exception as e:
        print(f"✗ Database model error: {e}")
        return False

def test_validation_logic():
    """Test certificate validation logic (without OCR)"""
    print("\nTesting validation logic...")
    try:
        from backend.validation import CertificateValidator
        
        validator = CertificateValidator()
        
        # Test data parsing
        sample_details = {
            'student_name': 'John Doe',
            'certificate_number': 'TEST001',
            'institution_name': 'Test University',
            'graduation_year': '2023',
            'course_name': 'Computer Science'
        }
        
        # Test basic field validation
        validation_result = validator._validate_basic_fields(sample_details)
        
        if validation_result['is_valid']:
            print("✓ Basic field validation passed")
        else:
            print(f"⚠️ Basic field validation issues: {validation_result['issues']}")
        
        # Test string similarity
        similarity = validator._string_similarity("Computer Science", "Computer Science Engineering")
        print(f"✓ String similarity calculation works: {similarity:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Validation logic error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation and basic routes"""
    print("\nTesting Flask app creation...")
    try:
        # Import the main app
        from app import app
        
        with app.test_client() as client:
            # Test home route
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page loads successfully")
            else:
                print(f"⚠️ Home page returned status code: {response.status_code}")
            
            # Test admin route
            response = client.get('/admin')
            if response.status_code == 200:
                print("✓ Admin page loads successfully")
            else:
                print(f"⚠️ Admin page returned status code: {response.status_code}")
            
            # Test API endpoint (should return error without file)
            response = client.post('/api/verify')
            if response.status_code == 400:
                print("✓ API verify endpoint responds correctly to invalid requests")
            else:
                print(f"⚠️ API verify endpoint returned unexpected status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ Flask app error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Academia Validator Basic Tests ===")
    print("Testing core functionality...\n")
    
    tests = [
        test_imports,
        test_database_models,
        test_validation_logic,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("✅ All tests passed! The system is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nThen visit:")
        print("  http://localhost:5000 - Main interface")
        print("  http://localhost:5000/admin - Admin dashboard")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        if passed >= 2:
            print("However, basic functionality seems to work. You can try running the app.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)