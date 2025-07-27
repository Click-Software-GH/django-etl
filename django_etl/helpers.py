# migration_core/etl_helpers.py

import re
import hashlib
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Dict, List, Union


class DataCleaner:
    """
    Collection of static methods for cleaning and transforming data
    """

    @staticmethod
    def clean_string(
        value: Any, max_length: Optional[int] = None, default: str = ""
    ) -> str:
        """
        Clean and sanitize string values

        Args:
            value: Input value to clean
            max_length: Maximum allowed length
            default: Default value if input is None/empty

        Returns:
            Cleaned string
        """
        if value is None:
            return default

        # Convert to string and strip whitespace
        cleaned = str(value).strip()

        # Replace multiple whitespaces with single space
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Remove null bytes and other problematic characters
        cleaned = cleaned.replace("\x00", "").replace("\r", "").replace("\n", " ")

        # Truncate if necessary
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].strip()

        return cleaned or default

    @staticmethod
    def clean_phone(phone: Any) -> Optional[str]:
        """
        Clean and format phone numbers

        Args:
            phone: Input phone number

        Returns:
            Cleaned phone number or None
        """
        if not phone:
            return None

        # Remove all non-digit characters
        digits = re.sub(r"\D", "", str(phone))

        # Return None if no digits found
        if not digits:
            return None

        # Format based on length
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        # Return as-is if unusual format
        return digits

    @staticmethod
    def clean_email(email: Any) -> Optional[str]:
        """
        Clean and validate email addresses

        Args:
            email: Input email address

        Returns:
            Cleaned email or None if invalid
        """
        if not email:
            return None

        cleaned = DataCleaner.clean_string(email).lower()

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(email_pattern, cleaned):
            return cleaned

        return None

    @staticmethod
    def parse_date(date_value: Any, formats: List[str] = None) -> Optional[date]:
        """
        Parse various date formats

        Args:
            date_value: Input date value
            formats: List of date formats to try

        Returns:
            Parsed date or None
        """
        if not date_value:
            return None

        if isinstance(date_value, (date, datetime)):
            return date_value.date() if isinstance(date_value, datetime) else date_value

        if formats is None:
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
                "%d-%m-%Y",
                "%Y%m%d",
            ]

        date_str = str(date_value).strip()

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_decimal(
        value: Any, default: Optional[Decimal] = None
    ) -> Optional[Decimal]:
        """
        Parse decimal values with error handling

        Args:
            value: Input value to parse
            default: Default value if parsing fails

        Returns:
            Parsed Decimal or default
        """
        if value is None:
            return default

        # Handle string values
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r"[$,]", "", value.strip())

            # Handle parentheses as negative
            if cleaned.startswith("(") and cleaned.endswith(")"):
                cleaned = "-" + cleaned[1:-1]

            value = cleaned

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return default

    @staticmethod
    def normalize_name(name: Any) -> Optional[str]:
        """
        Normalize person names

        Args:
            name: Input name

        Returns:
            Normalized name
        """
        if not name:
            return None

        # Clean the string
        cleaned = DataCleaner.clean_string(name)

        # Title case each word
        words = cleaned.split()
        normalized_words = []

        for word in words:
            # Handle special cases like "McDonald", "O'Brien"
            if "'" in word:
                parts = word.split("'")
                word = "'".join([part.capitalize() for part in parts])
            elif word.lower().startswith("mc"):
                word = "Mc" + word[2:].capitalize()
            else:
                word = word.capitalize()

            normalized_words.append(word)

        return " ".join(normalized_words)


class IDMapper:
    """
    Utility class for managing ID mappings between legacy and new systems
    """

    def __init__(self):
        self.mappings: Dict[str, Dict[Any, Any]] = {}

    def add_mapping(self, table_name: str, legacy_id: Any, new_id: Any):
        """
        Add an ID mapping

        Args:
            table_name: Name of the table/entity
            legacy_id: Legacy system ID
            new_id: New system ID
        """
        if table_name not in self.mappings:
            self.mappings[table_name] = {}

        self.mappings[table_name][legacy_id] = new_id

    def get_mapping(self, table_name: str, legacy_id: Any, default: Any = None) -> Any:
        """
        Get mapped ID

        Args:
            table_name: Name of the table/entity
            legacy_id: Legacy system ID
            default: Default value if mapping not found

        Returns:
            Mapped ID or default
        """
        return self.mappings.get(table_name, {}).get(legacy_id, default)

    def has_mapping(self, table_name: str, legacy_id: Any) -> bool:
        """
        Check if mapping exists

        Args:
            table_name: Name of the table/entity
            legacy_id: Legacy system ID

        Returns:
            True if mapping exists
        """
        return legacy_id in self.mappings.get(table_name, {})

    def get_stats(self) -> Dict[str, int]:
        """
        Get mapping statistics

        Returns:
            Dictionary with mapping counts per table
        """
        return {table: len(mappings) for table, mappings in self.mappings.items()}


class DataValidator:
    """
    Collection of validation utilities
    """

    @staticmethod
    def validate_required_fields(
        instance: Any, required_fields: List[str]
    ) -> List[str]:
        """
        Validate that required fields are present and not empty

        Args:
            instance: Object to validate
            required_fields: List of required field names

        Returns:
            List of validation errors
        """
        errors = []

        for field in required_fields:
            if not hasattr(instance, field):
                errors.append(f"Missing field: {field}")
                continue

            value = getattr(instance, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"Required field is empty: {field}")

        return errors

    @staticmethod
    def validate_field_lengths(
        instance: Any, field_limits: Dict[str, int]
    ) -> List[str]:
        """
        Validate field lengths

        Args:
            instance: Object to validate
            field_limits: Dictionary mapping field names to max lengths

        Returns:
            List of validation errors
        """
        errors = []

        for field, max_length in field_limits.items():
            if hasattr(instance, field):
                value = getattr(instance, field)
                if value and len(str(value)) > max_length:
                    errors.append(
                        f"Field '{field}' exceeds max length {max_length}: {len(str(value))}"
                    )

        return errors

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email address to validate

        Returns:
            True if valid email format
        """
        if not email:
            return False

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class HashGenerator:
    """
    Utility for generating hashes for duplicate detection
    """

    @staticmethod
    def generate_record_hash(fields: Dict[str, Any]) -> str:
        """
        Generate a hash for a record based on specific fields

        Args:
            fields: Dictionary of field names and values

        Returns:
            MD5 hash string
        """
        # Sort fields to ensure consistent hash
        sorted_fields = sorted(fields.items())

        # Create string representation
        field_str = "|".join([f"{k}:{v}" for k, v in sorted_fields if v is not None])

        # Generate hash
        return hashlib.md5(field_str.encode("utf-8")).hexdigest()

    @staticmethod
    def find_duplicates(
        records: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, List[int]]:
        """
        Find duplicate records based on specific fields

        Args:
            records: List of record dictionaries
            fields: List of field names to use for duplicate detection

        Returns:
            Dictionary mapping hashes to list of record indices
        """
        hash_to_indices = {}

        for idx, record in enumerate(records):
            field_values = {field: record.get(field) for field in fields}
            record_hash = HashGenerator.generate_record_hash(field_values)

            if record_hash not in hash_to_indices:
                hash_to_indices[record_hash] = []

            hash_to_indices[record_hash].append(idx)

        # Return only actual duplicates (hash appears more than once)
        return {
            h: indices for h, indices in hash_to_indices.items() if len(indices) > 1
        }


# Transformation functions that can be used with transform_field method
def to_title_case(value: Any) -> str:
    """Transform value to title case"""
    return str(value).title() if value else ""


def to_upper_case(value: Any) -> str:
    """Transform value to uppercase"""
    return str(value).upper() if value else ""


def to_lower_case(value: Any) -> str:
    """Transform value to lowercase"""
    return str(value).lower() if value else ""


def strip_whitespace(value: Any) -> str:
    """Strip whitespace from value"""
    return str(value).strip() if value else ""


def remove_special_chars(value: Any) -> str:
    """Remove special characters, keep only alphanumeric and spaces"""
    if not value:
        return ""
    return re.sub(r"[^a-zA-Z0-9\s]", "", str(value))


def format_ssn(value: Any) -> Optional[str]:
    """Format SSN as XXX-XX-XXXX"""
    if not value:
        return None

    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    return None
