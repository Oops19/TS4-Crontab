#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


class CrontabConstant:
    MINUTE_MAX = 59
    HOUR_MAX = 23
    WEEKDAY_MAX = 6
    SEASON_MAX = 3
    MOON_PHASE_MAX = 7

    WEEKDAY_MAP = {
        'SU': 0,
        'MO': 1,
        'TU': 2,
        'WE': 3,
        'TH': 4,
        'FR': 5,
        'SA': 6,
    }

    # SeasonType
    SEASON_MAP = {
        'SUMMER': 0,
        'FALL': 1,
        'AUTUMN': 1,  # not supported
        'WINTER': 2,
        'SPRING': 3,
        'EASTER': 3,  # not supported
    }

    # LunarPhaseType()
    MOON_PHASE_MAP = {
        'NEW_MOON': 0,
        'WAXING_CRESCENT': 1,
        'FIRST_QUARTER': 2,
        'WAXING_GIBBOUS': 3,
        'FULL_MOON': 4,
        'WANING_GIBBOUS': 5,
        'THIRD_QUARTER': 6,
        'WANING_CRESCENT': 7,
    }
