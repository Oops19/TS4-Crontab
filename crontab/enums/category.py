#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2022 https://github.com/Oops19
#
from ts4lib.custom_enums.enum_types.custom_enum import CustomEnum


class CrontabCategory(CustomEnum):
    NONE = 0
    HOUR = 2 ** 0
    MINUTE = 2 ** 1
    WEEKDAY = 2 ** 2
    SEASON = 2 ** 3
    MOON_PHASE = 2 ** 4
