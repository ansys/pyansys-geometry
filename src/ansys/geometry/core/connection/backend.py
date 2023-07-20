"""Provides definitions about the backend type."""
from enum import Enum


class BackendType(Enum):
    """Provides an enum holding the different backend types available."""

    DISCOVERY = 0, "product", "discovery"
    SPACECLAIM = 1, "product", "spaceclaim"
    WINDOWS_SERVICE = 2, "service", "spaceclaim_headless"
    LINUX_SERVICE = 3, "service"
