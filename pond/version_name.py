from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Optional, Any, Union
import re

from pond.exceptions import InvalidVersionName


def _compare_classnames(this: Any, that: Any) -> int:
    a = this.__class__.__name__
    b = that.__class__.__name__
    return 0 if a == b else (-1 if a < b else 1)


class VersionName(ABC):
    """Base class for all kind of version names. It defines a way to sort them and compute the next
    one."""

    @classmethod
    def from_string(klass, version_name: str) -> 'VersionName':
        """Parses a string into a version name.

        Parameters
        ----------
        version_name: str
            Version name as a string that needs to be parsed

        Returns
        -------
        VersionName
            The parsed version name

        Raises
        ------
        InvalidVersionName
            If the version name cannot be parsed
        """
        # Only first-level subclasses for the moment, it should be sufficient
        # At the same time, we give up defining a version name priority, and will return the
        # first VersionName subclass that can parse the string
        subclasses = klass.__subclasses__()
        for subclass in subclasses:
            try:
                version = subclass.from_string(version_name)
                break
            except InvalidVersionName:
                pass
        else:
            raise InvalidVersionName(version_name)
        return version

    @abstractmethod
    def next(self) -> 'VersionName':
        """Compute the next version"""
        ...

    @abstractmethod
    def _partial_compare(self, that: 'VersionName') -> Optional[int]:
        ...

    def __cmp__(self, other: 'VersionName') -> int:
        cmp = self._partial_compare(other)
        return cmp if cmp is not None else _compare_classnames(self, other)

    def __eq__(self, other: Any) -> bool:
        return self._partial_compare(other) == 0

    def __ne__(self, other: Any) -> bool:
        return self._partial_compare(other) != 0

    def __lt__(self, other: Any) -> bool:
        return self.__cmp__(other) < 0

    def __le__(self, other: Any) -> bool:
        return self.__cmp__(other) <= 0

    def __gt__(self, other: Any) -> bool:
        return self.__cmp__(other) > 0

    def __ge__(self, other: Any) -> bool:
        return self.__cmp__(other) >= 0

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{str(self)}")'


class SimpleVersionName(VersionName):
    """Simple version name are just an integer number (greater than 0) prefixed with "v" when
    rendered as string."""
    _FORMAT = re.compile('^v?([1-9][0-9]*)$')

    @classmethod
    def from_string(klass, version_name: str) -> 'SimpleVersionName':
        match = SimpleVersionName._FORMAT.match(version_name)
        if not match:
            raise InvalidVersionName(version_name)
        return klass(int(match[1]))

    def __init__(self, version_number: int):
        self.version_number = version_number

    def __hash__(self) -> int:
        return hash(self.version_number)

    def next(self) -> VersionName:
        return SimpleVersionName(self.version_number + 1)

    def _partial_compare(self, other: VersionName) -> Optional[int]:
        if isinstance(other, SimpleVersionName):
            return 0 if self.version_number == other.version_number else (
                -1 if self.version_number < other.version_number else 1)
        return None

    def __str__(self) -> str:
        return f'v{self.version_number}'


class DateTimeVersionName(VersionName):
    """DateTime version names are versions in the form of an ISO date time with space as a time
    separator (eg. "2020-01-02 03:04:05")"""
    @classmethod
    def from_string(klass, version_name: str) -> 'DateTimeVersionName':
        try:
            return klass(datetime.fromisoformat(version_name))
        except ValueError:
            raise InvalidVersionName(version_name)

    def __init__(self, dt: Union[date, datetime] = datetime.now()):
        if not isinstance(dt, datetime):
            dt = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        self.dt = dt

    def __hash__(self) -> int:
        return hash(self.dt)

    def next(self) -> VersionName:
        return DateTimeVersionName(self.dt + timedelta(seconds=1))

    def _partial_compare(self, other: VersionName) -> Optional[int]:
        if isinstance(other, DateTimeVersionName):
            return 0 if self.dt == other.dt else (-1 if self.dt < other.dt else 0)
        return None

    def __str__(self) -> str:
        return self.dt.isoformat(sep=' ', timespec='seconds')


class RunVersionName(VersionName):
    """Run version names are composed by a run ID and a version number."""

    _FORMAT = re.compile('^run_([A-Za-z0-9_]*)_v?([1-9][0-9]*)$')

    def __init__(self, run_id: str, version_number: int):
        self.run_id = run_id
        self.version_number = version_number

    # -- VersionName public interface

    @classmethod
    def from_string(klass, version_name: str) -> 'RunVersionName':
        match = klass._FORMAT.match(version_name)
        if not match:
            raise InvalidVersionName(version_name)
        run_id = match.group(1)
        version_number = int(match.group(2))
        return klass(run_id=run_id, version_number=version_number)

    def next(self) -> 'RunVersionName':
        return RunVersionName(run_id=self.run_id, version_number=self.version_number + 1)

    # -- VersionName protected interface

    def _partial_compare(self, other: VersionName) -> Optional[int]:
        if isinstance(other, RunVersionName):
            if self.run_id == other.run_id:
                return 0 if self.version_number == other.version_number else (
                    -1 if self.version_number < other.version_number else 1)
            else:
                return -1 if self.run_id < other.run_id else 1
        return None

    # -- Magic methods

    def __str__(self) -> str:
        return f'run_{self.run_id}_v{self.version_number}'

    def __hash__(self) -> int:
        return hash((self.run_id, self.version_number))
