from .database import Database, db

__all__ = ['Database', 'db']

from datetime import datetime
from flask import current_app

def relative_time(value):
    """Convert datetime string to 'X minutes ago', 'yesterday', etc."""
    if not value:
        return "unknown"
    try:
        # Parse SQLite datetime string
        dt = datetime.fromisoformat(value.replace(' ', 'T'))
        delta = datetime.utcnow() - dt
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 172800:
            return "yesterday"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''} ago"
    except Exception:
        return value  # fallback

# Register the filter
current_app.jinja_env.filters['relative_time'] = relative_time