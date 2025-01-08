from enum import Enum

class ProcessState(Enum):
    COMPLETED = 0
    FAILED = 1
    CANCELED = 2