import os

from src.schemas import VaultAccessRequest
from pydantic import ValidationError

class SecureVault:
    def __init__(self, vault_dir: str):
        self.vault_dir = vault_dir
        self.key = os.getenv("ENCRYPTION_KEY")

        # This is the 'Gate' that was missing coverage
        if not self.key or len(self.key) < 8:
            raise ValueError("Invalid or missing ENCRYPTION_KEY")
# testing stuff
    def _encrypt(self, text: str) -> str:
        """Simple Caesar shift based on key length."""
        shift = len(self.key) % 26
        return "".join(chr(ord(c) + shift) for c in text)

    def store_message(self, filename: str, message: str):
        """Encrypts a message and saves it to the specified vault directory."""
        if not os.path.exists(self.vault_dir):
            os.makedirs(self.vault_dir)

        path = os.path.join(self.vault_dir, filename)
        encrypted_content = self._encrypt(message)

        with open(path, "w") as f:
            f.write(encrypted_content)
        return path

def process_vault_entry(data: dict):
    try:
        # This line validates EVERYTHING instantly
        request = VaultAccessRequest(**data)
        print(f"Access granted for: {request.username}")
        return True
    except ValidationError as e:
        # Bandit and Ruff will like that we are handling the specific error
        print(f"SECURITY ALERT: Invalid Input Attempted: {e.json()}")
        return False

# Example usage for local manual testing only.
if __name__ == "__main__":  # pragma: no cover
    # This will FAIL (username too long, bad characters)
    malicious_payload = {"username": "admin_user_###_attack", "email": "not-an-email", "access_level": 99}
    process_vault_entry(malicious_payload)
