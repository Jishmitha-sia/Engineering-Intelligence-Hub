"""
Security utilities for Engineering Intelligence Hub.

Provides JWT token creation/validation and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
import bcrypt
import secrets
import string

from config import settings

BCRYPT_ROUNDS = 12


def create_access_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: User ID or email to encode in token
        expires_delta: Token expiration time (default from settings)
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Optional[dict]: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != "access":
            return None
            
        return payload
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def get_token_subject(token: str) -> Optional[str]:
    """
    Extract subject (user ID) from JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Optional[str]: User ID or None if token invalid
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    """
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS),
    )
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def generate_password_reset_token(email: str) -> str:
    """
    Generate password reset token.
    
    Args:
        email: User email address
        
    Returns:
        str: Password reset token
    """
    delta = timedelta(hours=1)  # Reset token expires in 1 hour
    expire = datetime.utcnow() + delta
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and extract email.
    
    Args:
        token: Password reset token
        
    Returns:
        Optional[str]: Email address or None if token invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != "password_reset":
            return None
            
        return payload.get("sub")
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def generate_email_verification_token(email: str) -> str:
    """
    Generate email verification token.
    
    Args:
        email: User email address
        
    Returns:
        str: Email verification token
    """
    delta = timedelta(days=1)  # Verification token expires in 1 day
    expire = datetime.utcnow() + delta
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify email verification token and extract email.
    
    Args:
        token: Email verification token
        
    Returns:
        Optional[str]: Email address or None if token invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != "email_verification":
            return None
            
        return payload.get("sub")
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def generate_secure_random_string(length: int = 32) -> str:
    """
    Generate cryptographically secure random string.
    
    Args:
        length: Length of string to generate
        
    Returns:
        str: Random string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def is_valid_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        tuple[bool, list[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    # Optional: Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password should contain at least one special character")
    
    return len(errors) == 0, errors


def create_api_key() -> str:
    """
    Generate API key for service-to-service authentication.
    
    Returns:
        str: API key
    """
    return f"eih_{generate_secure_random_string(40)}"


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key format and structure.
    
    Args:
        api_key: API key to verify
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Check format: eih_<40 character string>
    if not api_key.startswith("eih_"):
        return False
    
    if len(api_key) != 44:  # eih_ (4) + 40 characters
        return False
    
    # Check that suffix contains only valid characters
    suffix = api_key[4:]
    alphabet = string.ascii_letters + string.digits
    return all(c in alphabet for c in suffix)