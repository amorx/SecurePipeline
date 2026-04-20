import pytest
import os
from unittest.mock import patch, mock_open
from src.app import SecureVault, process_vault_entry
from src.schemas import VaultAccessRequest
from pydantic import ValidationError

# TEST 1: The Happy Path (Covers encryption and file writing)
@patch.dict(os.environ, {"ENCRYPTION_KEY": "super_secret_key"})
def test_vault_stores_encrypted_file():
    # We use a dummy directory name
    vault = SecureVault(vault_dir="test_vault")

    # Mock the 'open' function so no real file is created
    m = mock_open()
    with patch("builtins.open", m):
        # We also mock os.makedirs to avoid creating real folders
        with patch("os.makedirs"):
            vault.store_message("secret.txt", "Hello World")

    # Assertions to ensure the logic flowed correctly
    m.assert_called_once_with(os.path.join("test_vault", "secret.txt"), "w")
    handle = m()
    written_data = handle.write.call_args[0][0]
    assert written_data != "Hello World"  # Ensure it is encrypted

# TEST 2: The Error Path (This gets you from 94% to 100% coverage)
@patch.dict(os.environ, {"ENCRYPTION_KEY": "short"})
def test_vault_raises_error_on_weak_key():
    with pytest.raises(ValueError, match="Invalid or missing ENCRYPTION_KEY"):
        SecureVault(vault_dir="any_dir")

# TEST 3: Missing Key Path (Ensures security if env var is totally gone)
@patch.dict(os.environ, {}, clear=True)
def test_vault_raises_error_on_missing_key():
    with pytest.raises(ValueError, match="Invalid or missing ENCRYPTION_KEY"):
        SecureVault(vault_dir="any_dir")

# TEST 4: Data Validation (Pydantic integration)
def test_process_vault_entry_success():
    """Test that valid data passes the bouncer."""
    valid_data = {
        "username": "alex_2026",
        "email": "alex@example.com",
        "access_level": 3
    }
    assert process_vault_entry(valid_data) is True

def test_process_vault_entry_invalid_username():
    """Test security rejection for malicious characters in username."""
    # Attempting a basic SQL injection/XSS style character input
    invalid_data = {
        "username": "admin; DROP TABLE",
        "email": "alex@example.com",
        "access_level": 1
    }
    assert process_vault_entry(invalid_data) is False

def test_process_vault_entry_invalid_email():
    """Test that the email-validator integration works."""
    invalid_data = {
        "username": "alex",
        "email": "not-an-email",
        "access_level": 1
    }
    assert process_vault_entry(invalid_data) is False

def test_process_vault_entry_out_of_range_level():
    """Test that numerical constraints (ge=1, le=5) are enforced."""
    invalid_data = {
        "username": "alex",
        "email": "alex@example.com",
        "access_level": 10  # Out of range
    }
    assert process_vault_entry(invalid_data) is False

def test_schema_direct_validation():
    """Verify the Pydantic schema raises ValidationError directly."""
    with pytest.raises(ValidationError):
        VaultAccessRequest(
            username="a",  # Too short (min_length=3)
            email="test@test.com",
            access_level=1
        )

def test_username_validator_rejects_non_alnum_characters():
    """Directly exercise the custom validator rejection branch."""
    with pytest.raises(ValueError, match="Username must be alphanumeric"):
        VaultAccessRequest.username_alphanumeric("bad;name")
