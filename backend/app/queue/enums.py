from enum import StrEnum, auto


class TaskName(StrEnum):
    INGEST_COMPANY_DATA = auto()


class TaskStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETE = auto()
    FAILED = auto()
    ABORTED = auto()
