from enum import Enum

class MasteryCalculation(Enum):
    AVERAGE = 1
    DECAYING_AVERAGE = 2
    HIGHEST = 3
    HIGH_LAST_AVERAGE = 4
    MODE = 5
    NONE = 6
