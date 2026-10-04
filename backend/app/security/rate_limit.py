import time
from collections import defaultdict

from fastapi import Request, HTTPException, status


# Maximum requests allowed from one IP
MAX_REQUESTS = 60

# Time window in seconds
WINDOW_SECONDS = 60


request_history = defaultdict(list)


def rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"

    current_time = time.time()

    # Remove old requests
    request_history[client_ip] = [
        timestamp
        for timestamp in request_history[client_ip]
        if current_time - timestamp < WINDOW_SECONDS
    ]

    # Check limit
    if len(request_history[client_ip]) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    request_history[client_ip].append(current_time)