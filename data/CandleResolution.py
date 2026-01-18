from enum import Enum

class CandleResolution(Enum):
    DAY = "D"
    DAY_1 = "1D"

    SEC_5 = "5S"
    SEC_10 = "10S"
    SEC_15 = "15S"
    SEC_30 = "30S"
    SEC_45 = "45S"

    MIN_1 = "1"
    MIN_2 = "2"
    MIN_3 = "3"
    MIN_5 = "5"
    MIN_10 = "10"
    MIN_15 = "15"
    MIN_20 = "20"
    MIN_30 = "30"
    MIN_60 = "60"
    MIN_120 = "120"
    MIN_240 = "240"
