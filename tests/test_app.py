# tests/test_app.py
import pytest
from src.app import calculate_security_score

def test_score_calculation_success():
    # Test the standard logic
    assert calculate_security_score(100, 1.5) == 150.0

def test_score_calculation_negative_multiplier():
    # Test the safety gate (the ValueError)
    with pytest.raises(ValueError, match="Multiplier cannot be negative"):
        calculate_security_score(100, -1)
