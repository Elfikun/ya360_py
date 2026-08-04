import random
import string

def transliterate(text: str) -> str:
    """
    Transliterates Russian text to Latin based on simple mapping.
    """
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    text = text.lower()
    return ''.join(mapping.get(c, c) for c in text if c.isalpha())

def generate_nickname(last: str, first: str, middle: str) -> str:
    """
    Generates a nickname based on the rule:
    Last name + first letter of First name + first letter of Middle name in lowercase transliterated to Latin.
    Example: Иванов Иван Иванович -> ivanovii
    """
    last_trans = transliterate(last)
    first_trans = transliterate(first[0]) if first else ""
    middle_trans = transliterate(middle[0]) if middle else ""

    return f"{last_trans}{first_trans}{middle_trans}"

def generate_password(length: int = 12) -> str:
    """
    Generates a secure random password of specified length.
    Includes uppercase, lowercase, numbers, and special characters.
    """
    if length < 4:
        length = 12

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    all_chars = lower + upper + digits + special

    # Ensure at least one of each required type
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]

    # Fill the rest randomly
    password += [random.choice(all_chars) for _ in range(length - 4)]

    random.shuffle(password)
    return "".join(password)
