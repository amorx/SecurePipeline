##import pytest
import os
from unittest.mock import patch, mock_open
from src.app import SecureVault

@patch.dict(os.environ, {"ENCRYPTION_KEY": "super_secret_key"})
def test_vault_stores_encrypted_file():
    vault = SecureVault(vault_dir="test_vault")
    
    # We "mock" the open function so it doesn't actually touch the disk
    m = mock_open()
    with patch("builtins.open", m):
        vault.store_message("secret.txt", "Hello World")
    
    # Verify 'open' was called with the right path and write mode
    m.assert_called_once_with(os.path.join("test_vault", "secret.txt"), "w")
    
    # Verify it wrote the ENCRYPTED version, not the plain text
    # (With key 'super_secret_key', length 16, shift is 16)
    handle = m()
    handle.write.assert_called_once()
    written_data = handle.write.call_args[0][0]
    assert written_data != "Hello World"
