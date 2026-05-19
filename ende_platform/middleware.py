import time
from collections import defaultdict
from django.http import HttpResponseForbidden
from django.conf import settings


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = defaultdict(list)

    def __call__(self, request):
        if request.method == 'POST' and request.path in settings.RATE_LIMITED_PATHS:
            ip = self._get_ip(request)
            now = time.time()
            window = settings.RATE_LIMIT_WINDOW
            max_requests = settings.RATE_LIMIT_MAX_REQUESTS
            self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
            if len(self.requests[ip]) >= max_requests:
                return HttpResponseForbidden('Too many requests. Try again later.')
            self.requests[ip].append(now)
        return self.get_response(request)

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
