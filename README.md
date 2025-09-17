# Academia Validator - Certificate Verification System

A comprehensive digital platform for authenticating and detecting fake degrees/certificates issued by higher education institutions across Jharkhand.

## 🎯 Overview

This MVP system provides:
- **OCR-based certificate analysis** - Extract key details from uploaded certificates
- **Database verification** - Cross-reference with institutional records
- **AI-powered validation** - Detect anomalies and tampering
- **Admin dashboard** - Manage institutions and view verification statistics
- **Secure file processing** - Handle PDF and image certificate formats

## 🏗️ Architecture

```
academia-validator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── backend/
│   ├── models.py         # Database models (SQLAlchemy)
│   ├── ocr_utils.py      # OCR and text extraction utilities
│   └── validation.py     # Certificate validation logic
├── templates/
│   ├── index.html        # Main verification interface
│   └── admin.html        # Admin dashboard
├── uploads/              # Temporary file storage
├── database/             # SQLite database files
└── static/              # CSS/JS assets (if needed)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for text extraction)

### Installation

1. **Install Tesseract OCR:**
   ```bash
   # Windows (using Chocolatey)
   choco install tesseract

   # Or download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - Main interface: http://localhost:5000
   - Admin dashboard: http://localhost:5000/admin

## 📋 Features

### Core MVP Features
- ✅ **Certificate Upload Interface** - Web form for uploading certificate files
- ✅ **OCR Text Extraction** - Extract text from PDF/image certificates
- ✅ **Basic Validation** - Compare against database records
- ✅ **Institution Management** - Add/manage educational institutions
- ✅ **Verification Results** - Display authenticity status with confidence score
- ✅ **Admin Dashboard** - Basic system management interface

### Supported File Formats
- PDF documents
- PNG images
- JPG/JPEG images
- TIFF images
- BMP images

## 🎮 Usage

### For Employers/Verifiers:
1. Navigate to the home page
2. Upload the certificate (drag & drop or click to browse)
3. Click "Verify Certificate"
4. Review the verification results with confidence score

### For Administrators:
1. Access `/admin` for the dashboard
2. View verification statistics and recent activity
3. Add new institutions to the database
4. Monitor system usage and trends

## 🔧 API Endpoints

### Certificate Verification
```http
POST /api/verify
Content-Type: multipart/form-data

Parameters:
- certificate: File (PDF/image)
```

### Institution Management
```http
GET /api/institutions
POST /api/institutions
Content-Type: application/json
```

### Verification Logs
```http
GET /api/verification-logs?page=1&per_page=20
```

## 🎯 Future Enhancements (Phase 2+)

### Phase 2 Features:
- **QR Code Integration** - Generate and verify QR codes on certificates
- **Blockchain Verification** - Immutable certificate records
- **Advanced OCR** - Support for handwritten text and complex layouts
- **Mobile App** - Android/iOS app for on-the-go verification
- **Bulk Verification** - Process multiple certificates simultaneously

### Phase 3 Features:
- **AI Fraud Detection** - Machine learning models for subtle tampering detection
- **Digital Watermarking** - Invisible watermarks for new certificates
- **API Integration** - Connect with university ERP systems
- **Multi-language Support** - Support for regional languages
- **Advanced Analytics** - Fraud pattern detection and reporting

### Security & Compliance:
- **Two-factor Authentication** - Secure admin access
- **Audit Trails** - Complete verification history logging
- **Data Encryption** - Encrypt sensitive student information
- **GDPR Compliance** - Data privacy and retention policies

## 🏛️ Database Schema

### Tables:
1. **institutions** - Educational institutions registry
2. **certificates** - Valid certificate records
3. **verification_logs** - All verification attempts
4. **admins** - Admin user accounts

## 🛡️ Security Features

- File type validation and size limits
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 templating)
- Secure file upload handling
- Input sanitization and validation

## 📊 Sample Data

The system includes sample institutions and certificates for testing:

### Institutions:
- Ranchi University (RU)
- Birla Institute of Technology (BIT)
- NIT Jamshedpur (NIT_JSR)

### Test Certificates:
- RU2023001 - John Doe (B.Tech Computer Science, 2023)
- BIT2022045 - Jane Smith (B.Tech Electronics, 2022)

## 🔄 Verification Process

1. **File Upload** - User uploads certificate file
2. **OCR Processing** - Extract text using Tesseract
3. **Data Parsing** - Extract key fields (name, cert number, etc.)
4. **Database Lookup** - Search for matching records
5. **Similarity Matching** - Calculate match confidence
6. **Result Generation** - Provide verification status
7. **Logging** - Record verification attempt

## 🎨 UI/UX Features

- **Responsive Design** - Works on desktop and mobile
- **Drag & Drop Upload** - Intuitive file upload
- **Real-time Progress** - Loading indicators during processing
- **Visual Results** - Color-coded verification status
- **Confidence Scoring** - Percentage-based reliability indicator

## 🐛 Troubleshooting

### Common Issues:

1. **Tesseract not found error:**
   - Ensure Tesseract is installed and in PATH
   - Update the path in `ocr_utils.py` if needed

2. **File upload failures:**
   - Check file size (max 16MB)
   - Verify file format is supported

3. **Database errors:**
   - Delete `database/academia_validator.db` to reset
   - Restart the application to recreate tables

## 📝 License

This project is developed for the Government of Jharkhand, Department of Higher and Technical Education.

## 👥 Contributing

This is a government project. For inquiries or contributions, please contact the Department of Higher and Technical Education, Jharkhand.

---

**Note:** This is an MVP (Minimum Viable Product) designed for initial testing and feedback. Additional features and security enhancements will be implemented in subsequent phases based on user requirements and government policies.