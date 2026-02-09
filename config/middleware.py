from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class DisableCSRFMiddleware(MiddlewareMixin):
    """
    Middleware pour désactiver CSRF sur les endpoints API
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
