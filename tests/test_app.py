import pytest
import os
from unittest.mock import patch, mock_open
from src.app import SecureVault

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
