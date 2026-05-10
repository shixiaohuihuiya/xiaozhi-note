"""
依赖注入
"""
from dependencies.auth import get_current_user, get_current_active_user, require_admin, require_superadmin, get_optional_user

__all__ = ["get_current_user", "get_current_active_user", "require_admin", "require_superadmin", "get_optional_user"]
