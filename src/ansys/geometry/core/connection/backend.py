"""Module providing definitions for the backend types."""
from enum import Enum, unique


@unique
class BackendType(Enum):
    """Provides an enum holding the available backend types."""

    DISCOVERY = 0
    SPACECLAIM = 1
    WINDOWS_SERVICE = 2
    LINUX_SERVICE = 3


class ApiVersions(Enum):
    """Provides an enum for all the compatibles API versions."""

    V_21 = 21
    V_22 = 22
    V_231 = 231
    V_232 = 232
    V_241 = LATEST = 241
