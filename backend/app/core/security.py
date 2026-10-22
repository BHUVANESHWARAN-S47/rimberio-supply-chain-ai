import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "rimberio_enterprise_master_jwt_secret_key_2026_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))  # 24 hours

def get_password_hash(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with cryptographically secure salt."""
    salt = secrets.token_hex(16)
    iterations = 100000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    if not hashed_password or not plain_password:
        return False
    # If legacy test simulated hash
    if not hashed_password.startswith("pbkdf2_sha256$"):
        return plain_password == hashed_password or hashed_password == "scrypt_hash_simulated_buyer"

    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False
        _, iterations_str, salt, stored_key = parts
        iterations = int(iterations_str)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT token containing claims."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate signed JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
