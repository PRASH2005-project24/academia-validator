from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class Institution(db.Model):
    """Educational Institution Model"""
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text)
    state = db.Column(db.String(50), default='Jharkhand')
    established_year = db.Column(db.Integer)
    verification_contact = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    certificates = db.relationship('Certificate', backref='institution', lazy=True)
    
    def __repr__(self):
        return f'<Institution {self.name}>'

class Certificate(db.Model):
    """Certificate Model"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_number = db.Column(db.String(100), unique=True, nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    roll_number = db.Column(db.String(50))
    course_name = db.Column(db.String(200), nullable=False)
    degree_type = db.Column(db.String(50))  # Bachelor, Master, Diploma, etc.
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa_percentage = db.Column(db.String(20))
    issue_date = db.Column(db.Date, nullable=False)
    
    # Institution reference
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    
    # Security fields
    certificate_hash = db.Column(db.String(64))  # SHA-256 hash
    qr_code_data = db.Column(db.Text)  # QR code content
    
    # Status
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def generate_hash(self):
        """Generate SHA-256 hash for certificate"""
        data = f"{self.certificate_number}_{self.student_name}_{self.roll_number}_{self.course_name}_{self.graduation_year}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def __repr__(self):
        return f'<Certificate {self.certificate_number}>'

class VerificationLog(db.Model):
    """Verification Log Model"""
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_number = db.Column(db.String(100))
    student_name = db.Column(db.String(200))
    institution_name = db.Column(db.String(200))
    verification_result = db.Column(db.String(20))  # Valid, Invalid, Suspicious
    confidence_score = db.Column(db.Float)
    extracted_text = db.Column(db.Text)
    
    # Verification details
    verified_by = db.Column(db.String(100))  # IP or user identifier
    verification_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # File details
    uploaded_filename = db.Column(db.String(200))
    file_hash = db.Column(db.String(64))
    
    def __repr__(self):
        return f'<VerificationLog {self.certificate_number}>'

class Admin(db.Model):
    """Admin User Model"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Admin {self.username}>'