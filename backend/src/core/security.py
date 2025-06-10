import os
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ======= Password Hashing =========
def hash_password(password: str) -> str:

    """
    Hash password by SHA256 + Salt
    """

    salt = secrets.token_hex(16) 
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, stored_password_hash = stored_hash.split(':')
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_password_hash
    
    except ValueError:
        return False

# ==== Session Management =======

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def create_session_data(user_id: str, username: str) -> dict:
    return {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days = 7)).isoformat()
    }

# ==== Utilities Function ========

def generate_verification_code(length: int = 6) -> str:
    """ Email Verification """
    return ''.join(secrets.choice('0123456789') for _ in range(len))

def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """ check strong password """
    feedback = []

    if len(password) < 8:
        feedback.append("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร")
    
    if not any(c.isupper() for c in password):
        feedback.append("ต้องมีอักษรพิมพ์ใหญ่อย่างน้อย 1 ตัว")
    
    if not any(c.islower() for c in password):
        feedback.append("ต้องมีอักษรพิมพ์เล็กอย่างน้อย 1 ตัว")
    
    if not any(c.isdigit() for c in password):
        feedback.append("ต้องมีตัวเลขอย่างน้อย 1 ตัว")

    is_strong = len(feedback) == 0

    if is_strong:
        feedback.append("รหัสผ่านแข็งแรงแล้ว !")

    return is_strong, feedback

# ======= Configuration =============

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-for-development-only")
SESSION_EXPIRE_DAYS = 7

# ====== Testing =============

if __name__ == "__main__":
    print("====== Testing Security System ========")

    # hashing Test
    password = "MyPassword123"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")

    # password verification
    is_valid = verify_password(password, hashed)
    print(f"Verification (Correct): {is_valid}")

    is_invalid = verify_password("WrongPassword", hashed)
    print(f"Verification (Wrong): {is_invalid}")

    # Session token Testing
    token = generate_session_token()
    print(f"Session token: {token}")

    # Session data Testing
    session_data = create_session_data("user123", "testuser")
    print(f"Session data: {session_data}")

    # Password Strength Testing
    strong, feedback = is_strong_password(password)
    print(f"Password Strength: {strong}, Feedback: {feedback}")

    print("\n✅ Security system working!")