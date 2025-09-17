from backend.models import Certificate, Institution, VerificationLog, db
from typing import Dict, Tuple, Optional
from datetime import datetime
import hashlib
import re
from sqlalchemy import or_

class CertificateValidator:
    def __init__(self):
        self.validation_rules = {
            'name_similarity_threshold': 0.8,
            'year_range_tolerance': 2,
            'min_confidence_score': 60.0
        }
    
    def validate_certificate(self, extracted_details: Dict, file_hash: str, 
                           uploaded_filename: str, user_ip: str) -> Dict:
        """Main validation function"""
        
        validation_result = {
            'status': 'Invalid',
            'confidence_score': 0.0,
            'details': {},
            'verification_log': None,
            'issues': []
        }
        
        try:
            # Step 1: Basic field validation
            basic_validation = self._validate_basic_fields(extracted_details)
            if not basic_validation['is_valid']:
                validation_result['issues'].extend(basic_validation['issues'])
                validation_result['status'] = 'Invalid'
                validation_result['confidence_score'] = 20.0
                
                # Log the failed validation
                self._log_verification(
                    extracted_details, validation_result, 
                    file_hash, uploaded_filename, user_ip
                )
                return validation_result
            
            # Step 2: Database lookup
            db_matches = self._find_database_matches(extracted_details)
            
            if not db_matches:
                validation_result['status'] = 'Not Found'
                validation_result['issues'].append('Certificate not found in database')
                validation_result['confidence_score'] = 25.0
            else:
                # Step 3: Detailed matching
                best_match = self._evaluate_matches(db_matches, extracted_details)
                
                if best_match:
                    validation_result['status'] = best_match['status']
                    validation_result['confidence_score'] = best_match['confidence']
                    validation_result['details'] = best_match['details']
                    validation_result['issues'] = best_match['issues']
                else:
                    validation_result['status'] = 'Suspicious'
                    validation_result['issues'].append('No strong matches found')
                    validation_result['confidence_score'] = 40.0
            
            # Log the verification
            log_entry = self._log_verification(
                extracted_details, validation_result,
                file_hash, uploaded_filename, user_ip
            )
            validation_result['verification_log'] = log_entry.id
            
        except Exception as e:
            validation_result['status'] = 'Error'
            validation_result['issues'].append(f'Validation error: {str(e)}')
            validation_result['confidence_score'] = 0.0
        
        return validation_result
    
    def _validate_basic_fields(self, details: Dict) -> Dict:
        """Validate basic field requirements"""
        issues = []
        
        # Check for minimum required fields
        required_fields = ['student_name', 'institution_name']
        for field in required_fields:
            if not details.get(field) or not details[field].strip():
                issues.append(f'Missing required field: {field}')
        
        # Validate graduation year format
        if details.get('graduation_year'):
            try:
                year = int(details['graduation_year'])
                current_year = datetime.now().year
                if year < 1950 or year > current_year + 1:
                    issues.append(f'Invalid graduation year: {year}')
            except ValueError:
                issues.append('Invalid graduation year format')
        
        # Validate name format
        if details.get('student_name'):
            name = details['student_name']
            if len(name) < 2 or not re.match(r'^[a-zA-Z\s\.]+$', name):
                issues.append('Invalid student name format')
        
        # Validate certificate number format (if present)
        if details.get('certificate_number'):
            cert_num = details['certificate_number']
            if len(cert_num) < 3 or not re.match(r'^[A-Z0-9\-/]+$', cert_num):
                issues.append('Invalid certificate number format')
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    def _find_database_matches(self, details: Dict) -> list:
        """Find potential matches in the database"""
        matches = []
        
        # Search by certificate number (exact match)
        if details.get('certificate_number'):
            cert_matches = Certificate.query.filter(
                Certificate.certificate_number == details['certificate_number'],
                Certificate.is_valid == True
            ).all()
            matches.extend(cert_matches)
        
        # Search by student name and other details
        if details.get('student_name') and not matches:
            name_matches = Certificate.query.filter(
                Certificate.student_name.ilike(f"%{details['student_name']}%"),
                Certificate.is_valid == True
            ).all()
            
            # Filter by additional criteria if available
            filtered_matches = []
            for match in name_matches:
                score = self._calculate_match_score(match, details)
                if score > 0.5:  # Minimum match threshold
                    filtered_matches.append(match)
            
            matches.extend(filtered_matches)
        
        return matches
    
    def _calculate_match_score(self, db_certificate: Certificate, extracted_details: Dict) -> float:
        """Calculate similarity score between database record and extracted details"""
        scores = []
        
        # Name similarity (using simple string comparison)
        if extracted_details.get('student_name') and db_certificate.student_name:
            name_similarity = self._string_similarity(
                extracted_details['student_name'].lower(),
                db_certificate.student_name.lower()
            )
            scores.append(name_similarity * 0.4)  # 40% weight for name
        
        # Institution match
        if extracted_details.get('institution_name') and db_certificate.institution:
            inst_similarity = self._string_similarity(
                extracted_details['institution_name'].lower(),
                db_certificate.institution.name.lower()
            )
            scores.append(inst_similarity * 0.3)  # 30% weight for institution
        
        # Year match
        if extracted_details.get('graduation_year') and db_certificate.graduation_year:
            year_diff = abs(int(extracted_details['graduation_year']) - db_certificate.graduation_year)
            year_score = max(0, 1 - (year_diff / 5))  # Allow 5 year tolerance
            scores.append(year_score * 0.2)  # 20% weight for year
        
        # Course match
        if extracted_details.get('course_name') and db_certificate.course_name:
            course_similarity = self._string_similarity(
                extracted_details['course_name'].lower(),
                db_certificate.course_name.lower()
            )
            scores.append(course_similarity * 0.1)  # 10% weight for course
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Simple string similarity calculation"""
        # Using Jaccard similarity for simplicity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _evaluate_matches(self, matches: list, extracted_details: Dict) -> Optional[Dict]:
        """Evaluate database matches and return the best one"""
        if not matches:
            return None
        
        best_match = None
        highest_score = 0.0
        
        for match in matches:
            score = self._calculate_match_score(match, extracted_details)
            
            if score > highest_score:
                highest_score = score
                best_match = {
                    'certificate': match,
                    'score': score,
                    'status': self._determine_status(score),
                    'confidence': score * 100,
                    'details': {
                        'matched_certificate': match.certificate_number,
                        'matched_student': match.student_name,
                        'matched_institution': match.institution.name,
                        'matched_year': match.graduation_year,
                        'match_score': score
                    },
                    'issues': self._identify_discrepancies(match, extracted_details)
                }
        
        return best_match if highest_score > 0.6 else None
    
    def _determine_status(self, score: float) -> str:
        """Determine validation status based on match score"""
        if score >= 0.9:
            return 'Valid'
        elif score >= 0.7:
            return 'Likely Valid'
        elif score >= 0.5:
            return 'Suspicious'
        else:
            return 'Invalid'
    
    def _identify_discrepancies(self, db_cert: Certificate, extracted: Dict) -> list:
        """Identify specific discrepancies between database and extracted data"""
        issues = []
        
        # Check name discrepancies
        if extracted.get('student_name') and db_cert.student_name:
            if extracted['student_name'].lower() != db_cert.student_name.lower():
                issues.append(f'Name mismatch: extracted "{extracted["student_name"]}" vs database "{db_cert.student_name}"')
        
        # Check year discrepancies
        if extracted.get('graduation_year') and db_cert.graduation_year:
            if abs(int(extracted['graduation_year']) - db_cert.graduation_year) > 1:
                issues.append(f'Year mismatch: extracted "{extracted["graduation_year"]}" vs database "{db_cert.graduation_year}"')
        
        # Check grade discrepancies (if available)
        if extracted.get('cgpa_percentage') and db_cert.cgpa_percentage:
            if extracted['cgpa_percentage'] != db_cert.cgpa_percentage:
                issues.append(f'Grade mismatch: extracted "{extracted["cgpa_percentage"]}" vs database "{db_cert.cgpa_percentage}"')
        
        return issues
    
    def _log_verification(self, extracted_details: Dict, validation_result: Dict,
                         file_hash: str, uploaded_filename: str, user_ip: str) -> VerificationLog:
        """Log the verification attempt"""
        log_entry = VerificationLog(
            certificate_number=extracted_details.get('certificate_number', 'Unknown'),
            student_name=extracted_details.get('student_name', 'Unknown'),
            institution_name=extracted_details.get('institution_name', 'Unknown'),
            verification_result=validation_result['status'],
            confidence_score=validation_result['confidence_score'],
            extracted_text=str(extracted_details),
            verified_by=user_ip,
            uploaded_filename=uploaded_filename,
            file_hash=file_hash
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry

# Helper function for quick validation
def validate_certificate_data(extracted_details: Dict, file_hash: str, 
                            uploaded_filename: str, user_ip: str = 'unknown') -> Dict:
    """Convenience function to validate certificate"""
    validator = CertificateValidator()
    return validator.validate_certificate(
        extracted_details, file_hash, uploaded_filename, user_ip
    )