"""AliJaddi Account — auth_model."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["AuthManager"]

if TYPE_CHECKING:
    from .auth import AuthManager


def __getattr__(name: str) -> Any:
    if name == "AuthManager":
        from .auth import AuthManager

        return AuthManager
    raise AttributeError(name)
