# src/app.py

import os

def encrypt_message(message: str) -> str:
    """
    Encrypts a message using a key stored in environment variables.
    """
    # 1. SECRET GATE: Ensure the key exists
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ConnectionError("ENCRYPTION_KEY not found in environment")

    # 2. LOGIC GATE: Prevent weak passwords
    if len(key) < 8:
        raise ValueError("Encryption key is too weak. Must be at least 8 chars.")

    # 3. TRANSFORMATION: Simple Caesar-style shift for demo purposes
    # In a real app, you'd use a library like 'cryptography'
    shift = len(key) % 26
    encrypted = "".join(chr((ord(char) + shift)) for char in message)
    
    return encrypted
