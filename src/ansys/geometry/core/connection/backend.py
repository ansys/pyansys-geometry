"""Provides definitions about the backend type."""
from enum import Enum


class BackendType(Enum):
    """Provides an enum holding the available backend types."""

    DISCOVERY = 0
    SPACECLAIM = 1
    WINDOWS_SERVICE = 2
    LINUX_SERVICE = 3
