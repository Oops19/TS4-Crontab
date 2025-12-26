#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from typing import Set, List
from typing import Dict

from crontab.modinfo import ModInfo
from ts4lib.utils.singleton import Singleton

from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class CrontabStore(object, metaclass=Singleton):

    def __init__(self):
        self.is_initialized = False

        self.cron_jobs: Dict[str, List] = dict()  # {'job_id': [callback, arguments, weekdays, seasons, moon_phases], ...}
        """ cron_jobs stores a list with all registered cron jobs """

        self.cron_job_schedules: Dict[int, Set[str]] = dict()  # {0..1439: ['job_id', 'job_id_2'], ...}
        """ cron_job_schedules stores a list of 1440 schedules and the assigned cron jobs (weekday, season and moon phase are ignored """

        self.crontab_lines: Dict = dict()  # {'job_id': 'crontab', ...}
        """ crontab_lines stores a list with all crontab lines """
