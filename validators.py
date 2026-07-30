"""
This module provides validation functions and custom error exceptions to verify 
user inputs like locations, dates, and activities before processing.

"""


import re

class InvalidLocationError(Exception):
    """Raised when location input contains invalid characters or is empty."""
    pass

class InvalidDateError(Exception):
    """Raised when date format does not match YYYY-MM-DD."""
    pass

class InvalidActivityError(Exception):
    """Raised when selected activity is not supported."""
    pass

def validate_location(location: str) -> str:
    """Cleans and validates location string, raises InvalidLocationError if invalid."""
    if not location or not isinstance(location, str):
        raise InvalidLocationError("Location cannot be empty.")
    
    cleaned = location.strip()
    if not cleaned:
        raise InvalidLocationError("Location cannot be empty whitespace.")
    
    if not re.match(r"^[a-zA-A\s,\'-]+$", cleaned):
        raise InvalidLocationError("Location contains invalid characters.")
    
    return cleaned

def validate_date(date_str: str) -> bool:
    """Checks format using regex matching YYYY-MM-DD."""
    if not isinstance(date_str, str):
        raise InvalidDateError("Date must be a string.")
    
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str.strip()):
        raise InvalidDateError("Date must be in YYYY-MM-DD format.")
    
    return True

def validate_activity(activity: str, allowed_activities: list) -> str:
    """Ensures chosen activity is within allowed list."""
    if not activity or not isinstance(activity, str):
        raise InvalidActivityError("Activity must be a non-empty string.")
    
    cleaned = activity.strip().lower()
    allowed_lower = [a.lower() for a in allowed_activities]
    
    if cleaned not in allowed_lower:
        raise InvalidActivityError(f"Activity '{activity}' is not supported. Allowed: {allowed_activities}")
    
    return cleaned
