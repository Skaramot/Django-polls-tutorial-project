import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden

class PollsLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            print(f"{request.method} {request.path} - {response.status_code} - {duration:.2f}s")
        return response

class VoteProtectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST' and 'vote' in request.path:
            # Prevent too frequent voting (max 10 votes per minute per IP)
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'vote_count_{ip}'
            vote_count = cache.get(cache_key, 0)
            
            if vote_count >= 10:
                return HttpResponseForbidden("Too many votes. Please wait a minute.")
            
            cache.set(cache_key, vote_count + 1, 60)  # 1 minute timeout
        return None

class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Track user activity for analytics
            cache_key = f'user_activity_{request.user.id}'
            cache.set(cache_key, time.time(), 300)  # 5 minute timeout
        return None