from functools import wraps
from flask import request, abort
from app.models import User
from flask_login import current_user

def permission_required(permissions):
    """
    Decorator Check if a user has the required permission(s).
    Accepts a single permission string or list/tuple
    """
    
    if isinstance(permissions, str):
        permissions = [permissions]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            if not current_user.is_authenticated:
                abort(401)
            
            has_any_perm = any(current_user.has_permission(perm) for perm in permissions)
            
            if not has_any_perm:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
