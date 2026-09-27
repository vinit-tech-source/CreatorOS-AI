"""
app/core/rate_limit.py

Rate limiting configuration using slowapi.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# Define the limiter, using the client IP address as the identifier.
# In a production setting with a reverse proxy, you might need a custom key function
# if X-Forwarded-For is required, but get_remote_address handles basic cases.
limiter = Limiter(key_func=get_remote_address)
