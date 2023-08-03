"""Provides definitions about the backend type."""

from enum import Enum


class BackendType(Enum):
    """Provides an enum holding the different backend types available."""

    DISCOVERY = 0
    SPACECLAIM = 1
    WINDOWS_SERVICE = 2
    LINUX_SERVICE = 3


class ApiVersions(Enum):
    """Provides an enum for all the compatibles API versions."""

    V_212 = 212
    V_222 = 222
    V_231 = 231
    V_232 = 232
    V_241 = 241
    latest = 241
