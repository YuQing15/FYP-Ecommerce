from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

# Middleware to reset user cookies when the cookie version changes.
class ResetCookiesMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check for matching version
        cookie_version = request.COOKIES.get('cookie_version')
        request.reset_cookies = cookie_version != settings.COOKIE_VERSION

    def process_response(self, request, response):
        if getattr(request, 'reset_cookies', False):
            # Clear all cookies by setting them to expire
            for key in request.COOKIES:
                response.delete_cookie(key)
            # Set new version
            response.set_cookie('cookie_version', settings.COOKIE_VERSION)
        return response