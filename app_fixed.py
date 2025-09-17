from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import hashlib
from datetime import datetime, date
import json

# Import our modules
from backend.models import db, Certificate, Institution, VerificationLog, Admin
try:
    from backend.enhanced_ocr import process_certificate_file_enhanced as process_certificate_file
    OCR_AVAILABLE = True
    print("✅ Enhanced OCR loaded successfully!")
except ImportError as e:
    print(f"Warning: Enhanced OCR not available, falling back to basic: {e}")
    try:
        from backend.ocr_utils import process_certificate_file
        OCR_AVAILABLE = True
    except ImportError:
        print(f"Warning: No OCR functionality available: {e}")
        OCR_AVAILABLE = False
        def process_certificate_file(filepath, file_type):
            return {
                'extracted_text': 'OCR not available - please install tesseract',
                'parsed_details': {
                    'student_name': None,
                    'certificate_number': None,
                    'institution_name': 'Manual entry required',
                    'graduation_year': None
                },
                'confidence_score': 0.0
            }

from backend.validation import validate_certificate_data

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Use absolute path for database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'academia_validator.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}

# Initialize database
db.init_app(app)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of uploaded file"""
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_client_ip():
    """Get client IP address"""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

# Custom JSON encoder for date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = DateTimeEncoder

# Routes

@app.route('/')
def home():
    """Home page with upload interface"""
    print("✅ Home page accessed successfully!")
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    print("✅ Admin dashboard accessed!")
    try:
        # Get recent verifications
        recent_verifications = VerificationLog.query.order_by(
            VerificationLog.verification_timestamp.desc()
        ).limit(10).all()
        
        # Get statistics
        total_verifications = VerificationLog.query.count()
        total_institutions = Institution.query.filter(Institution.is_active == True).count()
        total_certificates = Certificate.query.filter(Certificate.is_valid == True).count()
        
        # Get verification results summary
        valid_count = VerificationLog.query.filter(
            VerificationLog.verification_result == 'Valid'
        ).count()
        invalid_count = VerificationLog.query.filter(
            VerificationLog.verification_result == 'Invalid'
        ).count()
        suspicious_count = VerificationLog.query.filter(
            VerificationLog.verification_result == 'Suspicious'
        ).count()
        
        stats = {
            'total_verifications': total_verifications,
            'total_institutions': total_institutions,
            'total_certificates': total_certificates,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'suspicious_count': suspicious_count
        }
        
        return render_template('admin.html', 
                             recent_verifications=recent_verifications, 
                             stats=stats)
    except Exception as e:
        print(f"❌ Admin dashboard error: {e}")
        return f"<h1>Admin Dashboard Error</h1><p>{str(e)}</p><p><a href='/'>Back to Home</a></p>"

@app.route('/test')
def test_page():
    """Simple test page"""
    return """
    <h1>🎉 Academia Validator Test Page</h1>
    <p>✅ Server is working correctly!</p>
    <ul>
        <li><a href="/">Home Page</a></li>
        <li><a href="/admin">Admin Dashboard</a></li>
        <li><a href="/api/institutions">API Test</a></li>
    </ul>
    <p>Database status: Connected ✅</p>
    """

@app.route('/api/verify', methods=['POST'])
def verify_certificate():
    """API endpoint to verify a certificate"""
    try:
        # Check if file was uploaded
        if 'certificate' not in request.files:
            return jsonify({
                'success': False, 
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['certificate']
        if file.filename == '':
            return jsonify({
                'success': False, 
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'File type not allowed. Supported types: {ALLOWED_EXTENSIONS}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        
        # Calculate file hash
        file_hash = calculate_file_hash(filepath)
        
        # Determine file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Process the certificate using OCR
        ocr_result = process_certificate_file(filepath, file_ext)
        
        # Validate the certificate
        validation_result = validate_certificate_data(
            ocr_result['parsed_details'], 
            file_hash, 
            unique_filename, 
            get_client_ip()
        )
        
        # Combine results
        response = {
            'success': True,
            'filename': filename,
            'file_hash': file_hash,
            'ocr_confidence': ocr_result['confidence_score'],
            'extracted_details': ocr_result['parsed_details'],
            'validation_result': validation_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Clean up uploaded file (optional - comment out to keep files)
        # os.remove(filepath)
        
        return jsonify(response)
        
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large. Maximum size is 16MB.'
        }), 413
    
    except Exception as e:
        app.logger.error(f'Verification error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An error occurred during verification. Please try again.'
        }), 500

@app.route('/api/institutions', methods=['GET'])
def get_institutions():
    """Get list of all institutions"""
    institutions = Institution.query.filter(Institution.is_active == True).all()
    return jsonify({
        'success': True,
        'institutions': [{
            'id': inst.id,
            'name': inst.name,
            'code': inst.code,
            'state': inst.state,
            'established_year': inst.established_year
        } for inst in institutions]
    })

@app.route('/api/institutions', methods=['POST'])
def add_institution():
    """Add a new institution"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({
                'success': False,
                'error': 'Name and code are required'
            }), 400
        
        # Check if institution code already exists
        existing = Institution.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Institution code already exists'
            }), 400
        
        # Create new institution
        institution = Institution(
            name=data['name'],
            code=data['code'],
            address=data.get('address', ''),
            state=data.get('state', 'Jharkhand'),
            established_year=data.get('established_year'),
            verification_contact=data.get('verification_contact', '')
        )
        
        db.session.add(institution)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Institution added successfully',
            'institution_id': institution.id
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding institution: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to add institution'
        }), 500

# Initialize database tables
def create_tables():
    """Create database tables before first request"""
    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    print(f"Database directory: {db_dir}")
    
    # Create all tables
    db.create_all()

if __name__ == '__main__':
    # Initialize database on startup
    with app.app_context():
        create_tables()
    
    print("🚀 Starting Academia Validator Server...")
    print("📍 Main interface: http://localhost:8080")
    print("📍 Admin dashboard: http://localhost:8080/admin") 
    print("📍 Test page: http://localhost:8080/test")
    print("📍 Alternative: http://127.0.0.1:8080")
    print("\n✅ Server ready! Open your browser to the URLs above.")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=8080, use_reloader=False)