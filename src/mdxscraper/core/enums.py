from enum import IntEnum


class InvalidAction(IntEnum):
    Exit = 0
    Collect = 1
    OutputWarning = 2
    Collect_OutputWarning = 3


