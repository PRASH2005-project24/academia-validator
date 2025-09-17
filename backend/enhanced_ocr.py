import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import PyPDF2
import re
import io
import os
from typing import Dict, List, Optional, Tuple

class EnhancedCertificateOCR:
    """Enhanced OCR with advanced image processing capabilities"""
    
    def __init__(self):
        # Configure Tesseract path (auto-detect or use default)
        self.setup_tesseract()
        
        # OCR configuration for better accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:-/()[]'
        
    def setup_tesseract(self):
        """Auto-detect Tesseract installation"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract found at: {path}")
                return
                
        print("⚠️ Tesseract not found in common locations. Please ensure it's in PATH")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Advanced image preprocessing for better OCR accuracy"""
        
        # Read image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            # Fallback to PIL
            pil_img = Image.open(image_path)
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply multiple preprocessing techniques
        processed_images = []
        
        # 1. Original grayscale
        processed_images.append(("original", gray))
        
        # 2. Gaussian blur + threshold (good for noisy images)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_images.append(("gaussian_thresh", thresh1))
        
        # 3. Adaptive threshold (good for varying lighting)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        processed_images.append(("adaptive_thresh", adaptive))
        
        # 4. Morphological operations (good for text cleanup)
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
        processed_images.append(("morphological", morph))
        
        # 5. Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        processed_images.append(("enhanced_contrast", enhanced))
        
        # 6. Edge preservation filter
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        processed_images.append(("bilateral_filter", bilateral))
        
        return processed_images
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, str]:
        """Extract text using multiple preprocessing methods"""
        
        try:
            # Get all preprocessed versions
            processed_images = self.preprocess_image(image_path)
            
            results = {}
            best_confidence = 0
            best_text = ""
            
            for method_name, processed_img in processed_images:
                try:
                    # Convert numpy array back to PIL Image
                    pil_img = Image.fromarray(processed_img)
                    
                    # Extract text with confidence
                    text = pytesseract.image_to_string(pil_img, config=self.ocr_config)
                    
                    # Get confidence data
                    confidence_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in confidence_data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    results[method_name] = {
                        'text': text.strip(),
                        'confidence': avg_confidence,
                        'word_count': len(text.split())
                    }
                    
                    # Keep track of best result
                    if avg_confidence > best_confidence and len(text.strip()) > 10:
                        best_confidence = avg_confidence
                        best_text = text.strip()
                        
                    print(f"📊 Method '{method_name}': {avg_confidence:.1f}% confidence, {len(text.split())} words")
                    
                except Exception as e:
                    print(f"❌ Error with method '{method_name}': {str(e)}")
                    results[method_name] = {'text': '', 'confidence': 0, 'word_count': 0}
            
            # Return best result or fallback
            if best_text:
                print(f"✅ Best OCR result: {best_confidence:.1f}% confidence")
                return {
                    'text': best_text,
                    'confidence': best_confidence,
                    'methods_tried': len(processed_images),
                    'detailed_results': results
                }
            else:
                # Fallback to simple OCR
                simple_img = Image.open(image_path)
                if simple_img.mode != 'RGB':
                    simple_img = simple_img.convert('RGB')
                fallback_text = pytesseract.image_to_string(simple_img)
                
                return {
                    'text': fallback_text.strip(),
                    'confidence': 50.0,  # Default confidence
                    'methods_tried': 1,
                    'detailed_results': {'fallback': {'text': fallback_text.strip(), 'confidence': 50.0}}
                }
                
        except Exception as e:
            print(f"❌ OCR Error: {str(e)}")
            return {
                'text': f"OCR processing failed: {str(e)}",
                'confidence': 0.0,
                'methods_tried': 0,
                'detailed_results': {}
            }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Extract text from PDF with multiple methods"""
        
        results = {'text': '', 'confidence': 90.0, 'methods_tried': 1}
        
        try:
            # Method 1: Direct PDF text extraction
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n"
            
            if text.strip():
                results['text'] = text.strip()
                results['confidence'] = 95.0
                print(f"✅ PDF text extracted successfully: {len(text)} characters")
                return results
            
            # Method 2: Convert PDF to images and OCR (if direct extraction fails)
            print("📄 PDF text extraction failed, trying OCR on PDF images...")
            
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(pdf_path)
                combined_text = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Save temporarily and process with OCR
                    temp_path = f"temp_page_{page_num}.png"
                    img.save(temp_path)
                    
                    ocr_result = self.extract_text_from_image(temp_path)
                    combined_text += ocr_result['text'] + "\n"
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                results['text'] = combined_text.strip()
                results['confidence'] = 80.0
                results['methods_tried'] = 2
                
                doc.close()
                return results
                
            except ImportError:
                print("⚠️ PyMuPDF not installed, cannot OCR PDF images")
            except Exception as e:
                print(f"❌ PDF to image OCR failed: {str(e)}")
            
            # Method 3: Fallback message
            results['text'] = "PDF text extraction failed. Please ensure the PDF contains selectable text or install PyMuPDF for image-based OCR."
            results['confidence'] = 0.0
            
        except Exception as e:
            print(f"❌ PDF processing error: {str(e)}")
            results['text'] = f"PDF processing failed: {str(e)}"
            results['confidence'] = 0.0
            
        return results
    
    def parse_certificate_details(self, text: str) -> Dict[str, Optional[str]]:
        """Enhanced certificate parsing with better regex patterns"""
        
        details = {
            'student_name': None,
            'certificate_number': None,
            'roll_number': None,
            'course_name': None,
            'institution_name': None,
            'graduation_year': None,
            'cgpa_percentage': None,
            'degree_type': None,
            'issue_date': None
        }
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        text_lower = text.lower()
        
        # Enhanced student name patterns
        name_patterns = [
            r'(?:name|Name|NAME)[:\s]*([A-Z][a-zA-Z\s.]+?)(?:\s*(?:son|daughter|s/o|d/o|w/o)|\s*roll|\s*reg|\s*has|\s*is|\s*$)',
            r'(?:this is to certify that|certify that|certified that)\s*([A-Z][a-zA-Z\s.]+?)(?:\s*(?:son|daughter|s/o|d/o|w/o)|\s*roll|\s*reg|\s*has|\s*is)',
            r'(?:mr\.|ms\.|miss|shri|smt\.?)\s*([A-Z][a-zA-Z\s.]+?)(?:\s*(?:son|daughter|s/o|d/o|w/o)|\s*roll|\s*reg|\s*has|\s*is)',
            r'(?:student|candidate)\s*(?:name)?[:\s]*([A-Z][a-zA-Z\s.]+?)(?:\s*(?:roll|reg|has|is))'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not details['student_name']:
                name = match.group(1).strip()
                if len(name) > 2 and len(name.split()) >= 2:  # At least first and last name
                    details['student_name'] = name
                    break
        
        # Enhanced certificate number patterns
        cert_patterns = [
            r'(?:certificate|cert|graduation)\s*(?:no|number|#)[:\s]*([A-Z0-9/-]+)',
            r'(?:registration|reg)\s*(?:no|number|#)[:\s]*([A-Z0-9/-]+)',
            r'(?:serial|sr)\s*(?:no|number|#)[:\s]*([A-Z0-9/-]+)',
            r'(?:diploma|degree)\s*(?:no|number|#)[:\s]*([A-Z0-9/-]+)',
            r'(?:^|\s)([A-Z]{2,4}[\d/-]{4,})',  # Pattern like ABC123456 or XYZ/2023/001
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 4 and re.search(r'[A-Z]', match) and re.search(r'\d', match):
                    details['certificate_number'] = match.strip()
                    break
            if details['certificate_number']:
                break
        
        # Enhanced roll number patterns
        roll_patterns = [
            r'(?:roll|Roll|ROLL)\s*(?:no|number|#)?[:\s]*([A-Z0-9]+)',
            r'(?:student|Student|STUDENT)\s*(?:id|ID|no|number|#)[:\s]*([A-Z0-9]+)',
            r'(?:enrollment|Enrollment|ENROLLMENT)\s*(?:no|number|#)[:\s]*([A-Z0-9]+)',
            r'(?:admission|Admission|ADMISSION)\s*(?:no|number|#)[:\s]*([A-Z0-9]+)'
        ]
        
        for pattern in roll_patterns:
            match = re.search(pattern, text)
            if match:
                roll = match.group(1).strip()
                if len(roll) >= 4:  # Valid roll numbers are usually longer
                    details['roll_number'] = roll
                    break
        
        # Enhanced graduation year patterns
        current_year = 2024
        year_patterns = [
            r'(?:year|Year|YEAR|graduated|passed|completed)[:\s]*(\d{4})',
            r'(?:batch|Batch|BATCH)[:\s]*(?:of\s*)?(\d{4})',
            r'(?:session|Session|SESSION)[:\s]*(\d{4})',
            r'(?:class|Class|CLASS)\s*(?:of\s*)?(\d{4})'
        ]
        
        all_years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            all_years.extend([int(year) for year in matches if 1950 <= int(year) <= current_year + 2])
        
        # Also find standalone 4-digit years
        standalone_years = re.findall(r'\b(19[5-9]\d|20[0-4]\d)\b', text)
        all_years.extend([int(year) for year in standalone_years])
        
        if all_years:
            # Choose the most recent valid year
            details['graduation_year'] = str(max(all_years))
        
        # Enhanced course/degree patterns
        degree_patterns = [
            r'(Bachelor\s+of\s+[A-Za-z\s]+)',
            r'(Master\s+of\s+[A-Za-z\s]+)',
            r'(B\.?Tech\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(M\.?Tech\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(B\.?Sc\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(M\.?Sc\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(B\.?Com\.?\s*[A-Za-z\s]*)',
            r'(M\.?Com\.?\s*[A-Za-z\s]*)',
            r'(B\.?A\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(M\.?A\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(Diploma\s+in\s+[A-Za-z\s]+)',
            r'(PhD\.?\s*(?:in\s+)?[A-Za-z\s]*)',
            r'(Doctor\s+of\s+Philosophy\s*(?:in\s+)?[A-Za-z\s]*)'
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                course = match.group(1).strip()
                if len(course) > 5:  # Valid course names are longer
                    details['course_name'] = course
                    # Extract degree type
                    if any(word in course.lower() for word in ['bachelor', 'b.tech', 'b.sc', 'b.com', 'b.a']):
                        details['degree_type'] = 'Bachelor'
                    elif any(word in course.lower() for word in ['master', 'm.tech', 'm.sc', 'm.com', 'm.a']):
                        details['degree_type'] = 'Master'
                    elif 'diploma' in course.lower():
                        details['degree_type'] = 'Diploma'
                    elif any(word in course.lower() for word in ['phd', 'doctor']):
                        details['degree_type'] = 'PhD'
                    break
        
        # Enhanced CGPA/Grade patterns
        grade_patterns = [
            r'(?:CGPA|cgpa|Cgpa)[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)[:\s]*(?:CGPA|cgpa|Cgpa)',
            r'(?:percentage|Percentage|PERCENTAGE)[:\s]*(\d{2,3}\.?\d*)%?',
            r'(\d{2,3}\.?\d*)[:\s]*(?:%|percent|per cent)',
            r'(?:grade|Grade|GRADE)[:\s]*([A-F][+-]?|\d+\.?\d*)',
            r'(?:marks|Marks|MARKS)[:\s]*(\d+\.?\d*)'
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                grade = match.group(1).strip()
                try:
                    grade_float = float(grade)
                    if 0 <= grade_float <= 10:  # CGPA
                        details['cgpa_percentage'] = f"{grade_float} CGPA"
                    elif 0 <= grade_float <= 100:  # Percentage
                        details['cgpa_percentage'] = f"{grade_float}%"
                    break
                except ValueError:
                    if re.match(r'[A-F][+-]?', grade):  # Letter grade
                        details['cgpa_percentage'] = grade
                        break
        
        # Enhanced institution name extraction
        institution_keywords = ['university', 'college', 'institute', 'school', 'academy', 'center', 'centre']
        lines = text.split('\n')[:10]  # Check first 10 lines
        
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 10:  # Skip very short lines
                for keyword in institution_keywords:
                    if keyword in line_clean.lower():
                        # Clean up the institution name
                        inst_name = re.sub(r'[^\w\s]', ' ', line_clean)
                        inst_name = re.sub(r'\s+', ' ', inst_name).strip()
                        if len(inst_name) > 10:
                            details['institution_name'] = inst_name
                            break
                if details['institution_name']:
                    break
        
        # Date patterns
        date_patterns = [
            r'(?:date|Date|DATE)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:issued|Issued|ISSUED)[:\s]*(?:on\s*)?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1).strip()
                details['issue_date'] = date_str
                break
        
        return details
    
    def calculate_confidence_score(self, extracted_details: Dict[str, Optional[str]], ocr_confidence: float) -> float:
        """Enhanced confidence calculation"""
        
        # Base score from OCR confidence
        base_score = ocr_confidence * 0.4  # 40% weight for OCR confidence
        
        # Field completeness score
        total_fields = len(extracted_details)
        filled_fields = sum(1 for value in extracted_details.values() if value and value.strip())
        completeness_score = (filled_fields / total_fields) * 100 * 0.3  # 30% weight
        
        # Critical fields score
        critical_fields = ['student_name', 'certificate_number', 'institution_name']
        critical_filled = sum(1 for field in critical_fields 
                            if extracted_details.get(field) and extracted_details[field].strip())
        critical_score = (critical_filled / len(critical_fields)) * 100 * 0.3  # 30% weight
        
        # Bonus for specific patterns
        bonus = 0
        if extracted_details.get('graduation_year'):
            try:
                year = int(extracted_details['graduation_year'])
                if 1950 <= year <= 2030:
                    bonus += 5
            except:
                pass
                
        if extracted_details.get('cgpa_percentage'):
            bonus += 5
            
        if extracted_details.get('roll_number') and len(extracted_details['roll_number']) >= 4:
            bonus += 5
        
        final_score = base_score + completeness_score + critical_score + bonus
        return min(round(final_score, 2), 100.0)  # Cap at 100%

# Main processing function with enhanced capabilities
def process_certificate_file_enhanced(file_path: str, file_type: str) -> Dict:
    """Enhanced certificate processing function"""
    
    ocr = EnhancedCertificateOCR()
    
    print(f"🔄 Processing {file_type.upper()} file: {file_path}")
    
    # Extract text based on file type
    if file_type.lower() == 'pdf':
        ocr_result = ocr.extract_text_from_pdf(file_path)
        extracted_text = ocr_result['text']
        ocr_confidence = ocr_result['confidence']
    else:  # Image files
        ocr_result = ocr.extract_text_from_image(file_path)
        extracted_text = ocr_result['text']
        ocr_confidence = ocr_result['confidence']
    
    # Parse certificate details
    details = ocr.parse_certificate_details(extracted_text)
    
    # Calculate overall confidence score
    final_confidence = ocr.calculate_confidence_score(details, ocr_confidence)
    
    print(f"✅ Processing complete! Final confidence: {final_confidence}%")
    
    return {
        'extracted_text': extracted_text,
        'parsed_details': details,
        'confidence_score': final_confidence,
        'ocr_confidence': ocr_confidence,
        'processing_method': 'enhanced_ocr',
        'methods_tried': ocr_result.get('methods_tried', 1)
    }