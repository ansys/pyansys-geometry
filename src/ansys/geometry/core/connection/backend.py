"""Provides definitions about the backend type."""
from enum import Enum


class BackendType(Enum):
    """Provides an enum holding the different backend types available."""

    DISCOVERY = 0, "product", "discovery"
    SPACECLAIM = 1, "product", "spaceclaim"
    DMS = 2, "service", "spaceclaim_headless"
    GEOMETRY_SERVICE = 3, "service"
