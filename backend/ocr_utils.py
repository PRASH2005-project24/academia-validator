import pytesseract
from PIL import Image
import PyPDF2
import re
import io
from typing import Dict, List, Optional

class CertificateOCR:
    def __init__(self):
        # Configure Tesseract path (adjust based on installation)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(image, lang='eng')
            return text.strip()
        except Exception as e:
            print(f"Error in OCR extraction: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF certificate"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error in PDF text extraction: {str(e)}")
            return ""
    
    def parse_certificate_details(self, text: str) -> Dict[str, Optional[str]]:
        """Parse certificate text to extract key details"""
        details = {
            'student_name': None,
            'certificate_number': None,
            'roll_number': None,
            'course_name': None,
            'institution_name': None,
            'graduation_year': None,
            'cgpa_percentage': None,
            'degree_type': None
        }
        
        # Clean the text
        text = text.replace('\n', ' ').strip()
        
        # Extract student name patterns
        name_patterns = [
            r'(?:name|Name|NAME)[\s:]+([A-Z][a-zA-Z\s]+?)(?:\s|$)',
            r'(?:This is to certify that|certify that)\s+([A-Z][a-zA-Z\s]+?)(?:\s|,)',
            r'(?:Mr\.|Ms\.|Miss)\s+([A-Z][a-zA-Z\s]+?)(?:\s|,)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match and not details['student_name']:
                details['student_name'] = match.group(1).strip()
                break
        
        # Extract certificate number
        cert_patterns = [
            r'(?:Certificate|Cert|certificate)[\s#:No]+([A-Z0-9]+)',
            r'(?:Registration|Reg)[\s#:No]+([A-Z0-9]+)',
            r'(?:Serial|Sr)[\s#:No]+([A-Z0-9]+)'
        ]
        for pattern in cert_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['certificate_number'] = match.group(1).strip()
                break
        
        # Extract roll number
        roll_patterns = [
            r'(?:Roll|roll|ROLL)[\s#:No]+([A-Z0-9]+)',
            r'(?:Student|student)[\s#:No]+([A-Z0-9]+)',
            r'(?:ID|id)[\s#:No]+([A-Z0-9]+)'
        ]
        for pattern in roll_patterns:
            match = re.search(pattern, text)
            if match:
                details['roll_number'] = match.group(1).strip()
                break
        
        # Extract graduation year
        year_patterns = [
            r'(?:year|Year|YEAR)[\s:]+(\d{4})',
            r'(\d{4})(?:\s|$)',
            r'(?:batch|Batch|BATCH)[\s:]+(\d{4})'
        ]
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            for year in matches:
                if 1950 <= int(year) <= 2030:  # Valid graduation year range
                    details['graduation_year'] = year
                    break
        
        # Extract course/degree information
        degree_patterns = [
            r'(?:Bachelor|Master|Diploma|PhD|B\.Tech|M\.Tech|B\.Sc|M\.Sc|B\.Com|M\.Com|B\.A|M\.A)',
            r'(?:Engineering|Medicine|Science|Arts|Commerce|Management)'
        ]
        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['course_name'] = match.group(0)
                break
        
        # Extract CGPA/Percentage
        grade_patterns = [
            r'(?:CGPA|cgpa)[\s:]+(\d+\.\d+)',
            r'(\d+\.\d+)[\s]*(?:CGPA|cgpa)',
            r'(\d{2,3})[\s]*%',
            r'(\d{2,3})[\s]*(?:percent|percentage)'
        ]
        for pattern in grade_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['cgpa_percentage'] = match.group(1)
                break
        
        # Extract institution name (this is tricky, usually at the top)
        lines = text.split('\n')[:5]  # Check first few lines
        for line in lines:
            if any(word in line.lower() for word in ['university', 'college', 'institute', 'school']):
                details['institution_name'] = line.strip()
                break
        
        return details
    
    def calculate_confidence_score(self, extracted_details: Dict[str, Optional[str]]) -> float:
        """Calculate confidence score based on extracted details"""
        total_fields = len(extracted_details)
        filled_fields = sum(1 for value in extracted_details.values() if value and value.strip())
        
        base_score = (filled_fields / total_fields) * 100
        
        # Boost score for critical fields
        critical_fields = ['student_name', 'certificate_number', 'institution_name']
        critical_filled = sum(1 for field in critical_fields 
                            if extracted_details.get(field) and extracted_details[field].strip())
        
        critical_score = (critical_filled / len(critical_fields)) * 100
        
        # Weighted average: 60% base score + 40% critical fields score
        final_score = (base_score * 0.6) + (critical_score * 0.4)
        
        return round(final_score, 2)

# Usage example functions
def process_certificate_file(file_path: str, file_type: str) -> Dict:
    """Main function to process a certificate file"""
    ocr = CertificateOCR()
    
    # Extract text based on file type
    if file_type.lower() in ['pdf']:
        extracted_text = ocr.extract_text_from_pdf(file_path)
    else:  # Image files
        extracted_text = ocr.extract_text_from_image(file_path)
    
    # Parse certificate details
    details = ocr.parse_certificate_details(extracted_text)
    
    # Calculate confidence score
    confidence = ocr.calculate_confidence_score(details)
    
    return {
        'extracted_text': extracted_text,
        'parsed_details': details,
        'confidence_score': confidence
    }