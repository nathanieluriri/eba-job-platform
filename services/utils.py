import random
import string

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