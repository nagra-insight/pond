from enum import Enum, unique
from typing import TypeVar

DataType = TypeVar('DataType')


class Adapter:
    pass


@unique
class SaveMode(str, Enum):
    """Version write save modes"""

    #: If a version already exists, new partitions are added to the existing ones
    # todo: define what does it means for image artifacts
    APPEND = 'append'
    #: If a version already exists, it is first deleted and then written
    OVERWRITE = 'overwrite'
    #: If a version already exists, nothing happens, the new data is not written
    IGNORE = 'ignore'
    #: If a version already exists, an error is raised (this is generally the default behavior)
    ERROR_IF_EXISTS = 'errorifexists'
