# myapp/middleware.py

import time
import logging

logger = logging.getLogger('apps.accounts.middleware.TimingMiddleware')

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        total_time = end_time - start_time

        # Log the page load time
        logger.info(f"Page Load Time: {total_time:.2f} seconds - {request.path}")
        return response
