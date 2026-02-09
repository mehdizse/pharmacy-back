"""
Custom throttling classes for authentication endpoints
"""
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.response import Response
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle for login attempts to prevent brute force
    """
    scope = 'login'
    
    def __init__(self):
        super().__init__()
        self.rate = '5/minute'  # 5 attempts per minute
        self.num_requests = 5
        self.duration = 60
    
    def throttle_failure(self):
        """
        Log failed login attempts
        """
        logger.warning(f"Login throttling triggered for IP: {self.get_ident()}")
        cache.set(f"login_throttle_{self.get_ident()}", True, timeout=300)
    
    def get_cache_key(self, request, view):
        """
        Use IP address for throttling
        """
        # Store request reference for later use
        self._request = request
        return f"login_throttle_{self.get_ident()}"
    
    def get_ident(self):
        """
        Get client IP address
        """
        if hasattr(self, '_request'):
            x_forwarded_for = self._request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
            return self._request.META.get('REMOTE_ADDR', '')
        return 'unknown'


class AdminRateThrottle(SimpleRateThrottle):
    """
    Stricter throttling for admin endpoints
    """
    scope = 'admin'
    
    def __init__(self):
        super().__init__()
        self.rate = '200/hour'  # 200 requests per hour
        self.num_requests = 200
        self.duration = 3600


class SensitiveOperationThrottle(SimpleRateThrottle):
    """
    Very strict throttling for sensitive operations
    """
    scope = 'sensitive'
    
    def __init__(self):
        super().__init__()
        self.rate = '10/hour'  # 10 sensitive operations per hour
        self.num_requests = 10
        self.duration = 3600
