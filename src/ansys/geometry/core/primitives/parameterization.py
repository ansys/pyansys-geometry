from enum import Enum

from beartype import beartype as check_input_types

from ansys.geometry.core.typing import Real


class Interval:
    """
    Interval class that defines a range of values.

    Parameters
    ----------
    start : Real
        Start value of the interval.
    end : Real
        End value of the interval.
    """

    @check_input_types
    def __init__(self, start: Real, end: Real) -> None:
        if end < start:
            raise ValueError("Start value must be less than end value")

        self._start = start
        self._end = end

    @property
    def start(self) -> Real:
        """Start value of the interval."""
        return self._start

    @property
    def end(self) -> Real:
        """End value of the interval."""
        return self._end

    def is_open(self) -> bool:
        """If the interval is open (-inf, inf)."""
        return self.start == float("-inf") and self.end == float("inf")

    def is_closed(self) -> bool:
        """If the interval is closed. Neither value is inf or -inf."""
        return self.start > float("-inf") and self.end < float("inf")

    def get_span(self) -> Real:
        if not self.is_closed():
            raise ValueError("Interval must be closed to get the span.")

        return self.end - self.start


class ParamForm(Enum):
    """The form of the parameterization."""

    OPEN = 1
    CLOSED = 2
    PERIODIC = 3
    OTHER = 4


class ParamType(Enum):
    """The type of the parameterization."""

    LINEAR = 1
    CIRCULAR = 2
    OTHER = 3


class Parameterization:
    """Parameterization class describes the parameters of a given geometry."""

    @check_input_types
    def __init__(self, form: ParamForm, type: ParamType, interval: Interval) -> None:
        self._form = form
        self._type = type
        self._interval = interval

    @property
    def form(self) -> ParamForm:
        """The form of the parameterization."""
        return self._form

    @property
    def type(self) -> ParamType:
        """The type of the parameterization."""
        return self._type

    @property
    def interval(self) -> Interval:
        """The interval of the parameterization."""
        return self._interval
