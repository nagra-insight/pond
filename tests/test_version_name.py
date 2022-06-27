from datetime import datetime

from pond.version_name import (
    VersionName,
    SimpleVersionName,
    DateTimeVersionName,
)


def test_simple_version_name_from_string():
    name = VersionName.from_string('v1')
    assert isinstance(name, SimpleVersionName)
    assert str(name) == 'v1'


def test_simple_version_name_next():
    name = SimpleVersionName(37)
    assert name.next() == SimpleVersionName(38)


def test_date_time_version_name_from_string():
    name = VersionName.from_string('2020-01-22 01:02:03')
    assert isinstance(name, DateTimeVersionName)
    assert str(name) == '2020-01-22 01:02:03'


def test_date_time_version_name_next():
    name = DateTimeVersionName(datetime(2022, 6, 12, 1, 32, 11))
    expected = DateTimeVersionName(datetime(2022, 6, 12, 1, 32, 12))
    assert name.next() == expected


def test_ordering():
    versions = [
        "2018-12-04 03:28:12",
        "v1",
        "2018-01-01 10:00:12",
        "v10",
        "v2",
        "2018-01-01",
    ]
    names = sorted([VersionName.from_string(version) for version in versions])

    expected = [
        "2018-01-01 00:00:00",
        '2018-01-01 10:00:12',
        '2018-12-04 03:28:12',
        'v1',
        'v2',
        'v10',
    ]
    assert [str(name) for name in names] == expected
