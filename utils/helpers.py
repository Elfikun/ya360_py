import secrets
import string
import os
import getpass
import socket

def get_operator_id() -> str:
    """Returns the operator identity in DOMAIN\\username@HOSTNAME format."""
    domain = os.environ.get('USERDOMAIN', '')
    user = getpass.getuser()
    hostname = socket.gethostname()

    # If USERDOMAIN is not available (e.g., on non-Windows systems), just use username@HOSTNAME
    if domain:
        return f"{domain}\\{user}@{hostname}"
    else:
        return f"{user}@{hostname}"

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

def generate_password(length: int = 10) -> str:
    """
    Generates a random, readable 10-character password.
    Contains uppercase, lowercase, and digits in randomized/arbitrary positions.
    Excludes ambiguous characters (i, l, 1, L, o, 0, O) and special characters.
    """
    excluded = set("il1Lo0O")
    lower_chars = [c for c in string.ascii_lowercase if c not in excluded]
    upper_chars = [c for c in string.ascii_uppercase if c not in excluded]
    digit_chars = [c for c in string.digits if c not in excluded]

    # Guarantee at least 1 upper, 1 lower, 1 digit with randomized count
    num_upper = secrets.randbelow(3) + 1  # 1..3
    num_digits = secrets.randbelow(3) + 2  # 2..4
    num_lower = max(1, length - num_upper - num_digits)

    password_list = (
        [secrets.choice(upper_chars) for _ in range(num_upper)] +
        [secrets.choice(lower_chars) for _ in range(num_lower)] +
        [secrets.choice(digit_chars) for _ in range(num_digits)]
    )

    all_allowed = lower_chars + upper_chars + digit_chars
    while len(password_list) < length:
        password_list.append(secrets.choice(all_allowed))

    # Shuffle to ensure arbitrary positions for uppercase, lowercase, and digits
    # secrets doesn't have shuffle, use secrets.SystemRandom which is CSPRNG-backed
    rng = secrets.SystemRandom()
    rng.shuffle(password_list)
    return "".join(password_list)
