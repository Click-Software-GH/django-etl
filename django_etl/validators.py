"""
Advanced Data Validation Framework
Provides comprehensive data quality checks and validation rules
"""

import re
from datetime import datetime, date
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    field: str
    value: Any
    is_valid: bool
    severity: ValidationSeverity
    message: str
    rule_name: str


class DataQualityValidator:
    """Advanced data quality validation framework"""
    
    def __init__(self):
        self.rules = []
        self.results = []
    
    def add_rule(self, field: str, rule_func: Callable, severity: ValidationSeverity = ValidationSeverity.ERROR, message: str = "", name: str = ""):
        """Add a validation rule"""
        self.rules.append({
            'field': field,
            'rule_func': rule_func,
            'severity': severity,
            'message': message,
            'name': name or rule_func.__name__
        })
    
    def validate_record(self, record: Dict[str, Any]) -> List[ValidationResult]:
        """Validate a single record against all rules"""
        results = []
        
        for rule in self.rules:
            field = rule['field']
            value = record.get(field)
            
            try:
                is_valid = rule['rule_func'](value)
                result = ValidationResult(
                    field=field,
                    value=value,
                    is_valid=is_valid,
                    severity=rule['severity'],
                    message=rule['message'] or f"Validation failed for {field}",
                    rule_name=rule['name']
                )
                results.append(result)
                
            except Exception as e:
                result = ValidationResult(
                    field=field,
                    value=value,
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation error: {str(e)}",
                    rule_name=rule['name']
                )
                results.append(result)
        
        return results
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of records"""
        all_results = []
        summary = {
            'total_records': len(records),
            'valid_records': 0,
            'records_with_errors': 0,
            'records_with_warnings': 0,
            'validation_results': []
        }
        
        for i, record in enumerate(records):
            record_results = self.validate_record(record)
            all_results.extend(record_results)
            
            has_errors = any(r.severity == ValidationSeverity.ERROR and not r.is_valid for r in record_results)
            has_warnings = any(r.severity == ValidationSeverity.WARNING and not r.is_valid for r in record_results)
            
            if has_errors:
                summary['records_with_errors'] += 1
            elif has_warnings:
                summary['records_with_warnings'] += 1
            else:
                summary['valid_records'] += 1
        
        summary['validation_results'] = all_results
        return summary


class CommonValidationRules:
    """Collection of common validation rules"""
    
    @staticmethod
    def not_null(value) -> bool:
        """Check if value is not null/None"""
        return value is not None
    
    @staticmethod
    def not_empty_string(value) -> bool:
        """Check if string is not empty"""
        return value is not None and str(value).strip() != ""
    
    @staticmethod
    def email_format(value) -> bool:
        """Validate email format"""
        if not value:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, str(value)) is not None
    
    @staticmethod
    def phone_format(value) -> bool:
        """Validate phone number format"""
        if not value:
            return False
        # Simple phone validation - can be enhanced
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, str(value)) is not None and len(re.sub(r'\D', '', str(value))) >= 10
    
    @staticmethod
    def date_format(value, date_format: str = "%Y-%m-%d") -> bool:
        """Validate date format"""
        if not value:
            return False
        try:
            datetime.strptime(str(value), date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def numeric_range(min_val: float = None, max_val: float = None):
        """Create a numeric range validator"""
        def validator(value) -> bool:
            if value is None:
                return False
            try:
                num_val = float(value)
                if min_val is not None and num_val < min_val:
                    return False
                if max_val is not None and num_val > max_val:
                    return False
                return True
            except (ValueError, TypeError):
                return False
        return validator
    
    @staticmethod
    def string_length(min_len: int = None, max_len: int = None):
        """Create a string length validator"""
        def validator(value) -> bool:
            if value is None:
                return False
            str_val = str(value)
            if min_len is not None and len(str_val) < min_len:
                return False
            if max_len is not None and len(str_val) > max_len:
                return False
            return True
        return validator
    
    @staticmethod
    def regex_pattern(pattern: str):
        """Create a regex pattern validator"""
        def validator(value) -> bool:
            if value is None:
                return False
            return re.match(pattern, str(value)) is not None
        return validator
    
    @staticmethod
    def choices_validator(valid_choices: List[Any]):
        """Create a choices validator"""
        def validator(value) -> bool:
            return value in valid_choices
        return validator


class HealthcareValidationRules(CommonValidationRules):
    """Healthcare-specific validation rules"""
    
    @staticmethod
    def patient_id_format(value) -> bool:
        """Validate patient ID format (alphanumeric, specific length)"""
        if not value:
            return False
        pattern = r'^[A-Z0-9]{6,12}$'
        return re.match(pattern, str(value)) is not None
    
    @staticmethod
    def medical_record_number(value) -> bool:
        """Validate medical record number"""
        if not value:
            return False
        # Remove any separators and check if numeric
        clean_value = re.sub(r'[\-\s]', '', str(value))
        return clean_value.isdigit() and len(clean_value) >= 6
    
    @staticmethod
    def age_range(value) -> bool:
        """Validate age is within reasonable range"""
        if value is None:
            return False
        try:
            age = int(value)
            return 0 <= age <= 150
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def gender_format(value) -> bool:
        """Validate gender format"""
        if not value:
            return False
        valid_genders = ['M', 'F', 'Male', 'Female', 'Other', 'U', 'Unknown']
        return str(value).strip().title() in [g.title() for g in valid_genders]
    
    @staticmethod
    def blood_type_format(value) -> bool:
        """Validate blood type format"""
        if not value:
            return True  # Optional field
        valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        return str(value).upper().strip() in valid_types
