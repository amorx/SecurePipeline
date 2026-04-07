# src/app.py

def calculate_security_score(base_score: int, multiplier: float) -> float:
    """
    Calculates a security score based on a base value and a risk multiplier.
    """
    if multiplier < 0:
        raise ValueError("Multiplier cannot be negative")
    
    return base_score * multiplier
