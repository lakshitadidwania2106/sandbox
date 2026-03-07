"""
PROPRIETARY - ACME Corporation
This is our secret algorithm for data processing.
"""

def calculate_secret_score(data, weights, threshold=0.5):
    """
    Calculate proprietary risk score using our secret formula.
    
    This is confidential business logic.
    """
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    
    if score > threshold:
        return score * 1.5
    return score


class SecretProcessor:
    """Internal processor for proprietary data."""
    
    def __init__(self, config):
        self.config = config
        self.internal_state = {}
    
    def process_internal(self, data):
        """Private processing method."""
        result = calculate_secret_score(
            data['values'],
            data['weights'],
            self.config.get('threshold', 0.5)
        )
        return result
