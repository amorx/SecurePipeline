# tests/test_app.py

import pytest
import os
from unittest.mock import patch
from src.app import encrypt_message

# HAPPY PATH
@patch.dict(os.environ, {"ENCRYPTION_KEY": "super_secret_key"})
def test_encryption_success():
    result = encrypt_message("Hello")
    assert result != "Hello"
    assert isinstance(result, str)

# ERROR PATH: MISSING KEY
@patch.dict(os.environ, {}, clear=True)
def test_encryption_fails_missing_key():
    with pytest.raises(ConnectionError, match="ENCRYPTION_KEY not found"):
        encrypt_message("Hello")

# ERROR PATH: WEAK KEY
@patch.dict(os.environ, {"ENCRYPTION_KEY": "123"})
def test_encryption_fails_weak_key():
    with pytest.raises(ValueError, match="key is too weak"):
        encrypt_message("Hello")
