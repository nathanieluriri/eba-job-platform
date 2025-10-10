import random
import string
from typing import List,Dict,Any
def generate_random_string(length: int = 16) -> str:
    """
    Generate a random alphanumeric string of given length.

    Args:
        length (int): Length of the string to generate (default: 16).
    
    Returns:
        str: Random alphanumeric string.
    """
    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(random.choice(characters) for _ in range(length))


def generate_random_string_digits_only(length: int = 16) -> str:
    """
    Generate a random alphanumeric string of given length.

    Args:
        length (int): Length of the string to generate (default: 16).
    
    Returns:
        str: Random alphanumeric string.
    """
    characters =  string.digits  # 0-9
    return ''.join(random.choice(characters) for _ in range(length))


def format_pydantic_errors(errors: List[Dict[str, Any]]) -> str:
    """Converts a list of Pydantic error dicts into a concise, human-readable string."""
    messages = []
    for error in errors:
        # Get the field name, handling potential tuple structure
        loc = error.get('loc', ('Unknown Field',))
        field_name = str(loc[-1]) 
        
        # Get the error message
        msg = error.get('msg', 'Validation Error')
        
        # Format the message
        messages.append(f"Field '{field_name}': {msg}")
        
    return "Validation Error(s): " + " | ".join(messages)