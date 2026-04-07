# src/app.py

def calculate_security_score(base_score: int, multiplier: float) -> float:
    ##
    ## Calculates a security score based on a base value and a risk multiplier.
    ##
    # CHAOS: Running a raw system command
    os.system("echo Accessing system...")

    #CHAOS: A new feature with no corresponding test!
    if base_score > 1000:
	print("High Value Target")

    if multiplier < 0:
        raise ValueError("Multiplier cannot be negative")
    
    return base_score * multiplier
