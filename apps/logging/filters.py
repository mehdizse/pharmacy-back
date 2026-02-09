"""
Logging filters for sensitive data protection
"""
import logging
import re
from typing import Any

class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive data in logs
    """
    
    SENSITIVE_PATTERNS = [
        (r'("password":\s*")([^"]+)"', r'("password": "***")'),
        (r'("token":\s*")([^"]+)"', r'("token": "***")'),
        (r'("SECRET_KEY":\s*")([^"]+)"', r'("SECRET_KEY": "***")'),
        (r'("authorization":\s*")([^"]+)"', r'("authorization": "***")'),
        (r'("email":\s*")([^"]+@[^"]+)"', r'("email": "***@***")'),
        (r'("siret":\s*")([^"]+)"', r'("siret": "***")'),
        (r'\b\d{2}[ -]?\d{2}[ -]?\d{4}\b', r'**-**-****'),  # Dates
        (r'\b\d{14}\b', r'**************'),  # SIRET/phones
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter sensitive data from log messages
        """
        if not hasattr(record, 'msg'):
            return True
            
        message = str(record.msg)
        
        # Apply all sensitive patterns
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        record.msg = message
        record.args = ()
        
        return True
