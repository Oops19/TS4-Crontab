#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import re
from typing import Set

from crontab.store.crontab_o import CrontabO
from crontab.store.crontab_store import CrontabStore
import importlib
import time
from typing import List, Union

from crontab.enums.category import CrontabCategory
from crontab.enums.constants import CrontabConstant
from crontab.modinfo import ModInfo
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class ManageCrontab:

    def __init__(self):
        self.cs = CrontabStore()

    def add_crontab_line(self, crontab_line, save_data: bool = True) -> str:
        """ Add a job to crontab. """
        r1 = re.compile("^ +| +$")  # replace leading and trailing space
        r2 = re.compile("  +")  # replace multiple spaces with one
        r3 = re.compile("^([^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+) (.+)$")  # parse '* * * * * nop arg1 arg2'
        r4 = re.compile("^([^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+) ([^#]+) # (.+)$")  # parse '* * * * * nop arg1 arg2 # comment'

        def _upper(match: re.Match) -> str:
            return match.group(1)[1].upper()

        crontab_line_2 = re.sub(r1, "", crontab_line)
        crontab_line_2 = re.sub(r2, " ", crontab_line_2)
        if '#' in crontab_line_2:
            matches = re.match(r4, crontab_line_2)
        else:
            matches = re.match(r3, crontab_line_2)
        if matches and matches.groups():
            times = matches.group(1).upper()
            command, arg_str = f"{matches.group(2)} ".split(' ', 1)
            if command == 'nop':
                command = 'crontab.ui.crontab_ui.CrontabUI.nop'
            else:
                command = re.sub(r'(\^[a-z])', _upper, command)
            if arg_str:
                _args = arg_str.strip().split(' ')
            else:
                _args = []
            if len(matches.groups()) == 3:
                job_id = matches.group(3)
            else:
                job_id = None

            job_id = self.add_job(times, command, _args, job_id=job_id, save_data=save_data)
            log.debug(f"Added job as '{job_id}'")
            self.cs.crontab_lines.update({job_id: crontab_line})
            return job_id
        else:
            log.debug(f"Could not process '{crontab_line}'")

    def add_job(self, crontab_times, callback: str, args: Union[List, None] = None, job_id: str = None, save_data: bool = True) -> str:
        """
        Add a job to crontab.
        :param crontab_times: The string to define the times (minutes hours weekdays seasons moon_phases)
        :param callback: callback method. '^x' is converted to 'X' to be able to use cheat commands which are all lower case.
        :param args: List with arguments, [] or None for no arguments
        :param job_id: Unique name/ID of the job, generated if not specified
        :param save_data: Set to 'False' to persist the entry on disk and reload later (not yet supported)
        :return: Returns the job_id or None if the job could not be added.
        """
        log.debug(f"add_job({crontab_times}, {callback}, {args}, {job_id}, {save_data})")
        if not job_id:
            job_id = f"t{int(time.time() * 1000)}"
        if not args:
            args = []

        try:
            _class_string, _function_name = callback.rsplit('.', 1)
            _module_name, _class_name = _class_string.rsplit('.', 1)
            _class = getattr(importlib.import_module(_module_name), _class_name)
            _function = getattr(_class, _function_name)
        except Exception as e:
            log.error(f"Error '{e} - Could not add '{callback}'", throw=False)
            #  'module 'crontab.ui' has no attribute 'CrontabUI' - Could not add 'crontab.ui.CrontabUI.nop'
            return ''

        mm, hh, wd, ss, mp = crontab_times.split(' ', 5)
        minutes: List = self._parse_time(mm, CrontabCategory.MINUTE)
        hours: List = self._parse_time(hh, CrontabCategory.HOUR)
        weekdays: List = self._parse_time(wd, CrontabCategory.WEEKDAY)
        seasons: List = self._parse_time(ss, CrontabCategory.SEASON)
        moon_phases: List = self._parse_time(mp, CrontabCategory.MOON_PHASE)
        self.cs.cron_jobs.update({job_id: [_function, args, weekdays, seasons, moon_phases]})  # () vs [] TODO ????

        cron_job_schedules = self.cs.cron_job_schedules
        for hour in hours:
            for minute in minutes:
                _et = hour * 60 + minute
                jobs: Set = cron_job_schedules.get(_et, set())
                jobs.add(job_id)
                log.debug(f"@({_et}) -> '{jobs}'")
                cron_job_schedules.update({_et: jobs})

        # Sort dict
        self.cs.cron_job_schedules = {key: cron_job_schedules[key] for key in sorted(cron_job_schedules.keys())}  # = dict(sorted(cron_job_schedules.items()))
        if save_data:
            co = CrontabO()
            co.save()

        log.debug(f"add_job() -> {job_id}")
        return job_id

    def remove_job(self, job_id: str, save_data: bool = True) -> bool:
        """
        Remove a job from crontab.
        :param job_id: The job_id to delete
        :return: True for success, otherwise false
        """
        try:
            del self.cs.cron_jobs[job_id]
            del self.cs.crontab_lines[job_id]
            to_delete = set()
            for _time, job_ids in self.cs.cron_job_schedules.items():
                if job_id in job_ids:
                    job_ids.remove(job_id)
                    self.cs.cron_job_schedules.update({_time: job_ids})
                    if not job_ids:
                        to_delete.add(_time)
            for _time in to_delete:
                del self.cs.cron_job_schedules[_time]
            if save_data:
                co = CrontabO()
                co.save()
            return True
        except:
            return False

    def _get_int(self, value: str, replacement_map: dict) -> int:
        """
        Convert a 'str' to 'int'
        :param value: The value to convert to int
        :param replacement_map: A dict with `{'str': nr}` to replace a value starting with 'str' to. value 'Fun' with `{'Fu': 7}` returns `7`.
        :return: Int value of 'value' or 0 if conversion failed.
        """
        return_value = 0
        if value.isdigit():
            return_value = int(value)
        elif replacement_map:
            for k, v in replacement_map.items():
                if value == k:
                    return_value = v
                    break
        return return_value

    def _parse_time(self, crontab_time: str, category: CrontabCategory = CrontabCategory.NONE, start_value: int = 0, end_value: int = -1):
        """
        Parse a crontab time entry (*, m/n, m-n, m, m,n,...) for hour, minute, weekday, season or moon phase.
        :param crontab_time:
        :param category: optionally CrontabCategory to define replacements and start/stop values
        :param start_value: custom start value when CrontabCategory.NONE is used
        :param end_value: custom end value when CrontabCategory.NONE is used
        :return:
        """
        log.debug(f"_parse_time({crontab_time}, {category}, {start_value}, {end_value})")
        if start_value < 0:
            start_value = 0
        times = []
        replacement_map = None
        if category == CrontabCategory.MINUTE:
            if end_value < 0 or end_value > CrontabConstant.MINUTE_MAX:
                end_value = CrontabConstant.MINUTE_MAX
        elif category == CrontabCategory.HOUR:
            if end_value < 0 or end_value > CrontabConstant.HOUR_MAX:
                end_value = CrontabConstant.HOUR_MAX
        elif category == CrontabCategory.WEEKDAY:
            if end_value < 0 or end_value > CrontabConstant.WEEKDAY_MAX:
                end_value = CrontabConstant.WEEKDAY_MAX
            replacement_map = CrontabConstant.WEEKDAY_MAP
        elif category == CrontabCategory.SEASON:
            if end_value < 0 or end_value > CrontabConstant.SEASON_MAX:
                end_value = CrontabConstant.SEASON_MAX
            replacement_map = CrontabConstant.SEASON_MAP
        elif category == CrontabCategory.MOON_PHASE:
            if end_value < 0 or end_value > CrontabConstant.MOON_PHASE_MAX:
                end_value = CrontabConstant.MOON_PHASE_MAX
            replacement_map = CrontabConstant.MOON_PHASE_MAP
        if start_value > end_value:
            return times

        if crontab_time == '*':
            times = list(range(start_value, end_value + 1))
        elif '/' in crontab_time:
            _start_str, _div_str = crontab_time.split('/')
            start = self._get_int(_start_str, replacement_map)
            div = self._get_int(_div_str, replacement_map)
            for i in range(0, end_value - start):
                if i % div == 0:
                    times.append(i + start)
        elif '-' in crontab_time:
            _start_str, _end_str = crontab_time.split('-')
            start = self._get_int(_start_str, replacement_map)
            end = self._get_int(_end_str, replacement_map) + 1  # include the last element. For 1-2 '2' should be included!
            times = list(range(start, end))
        elif ',' in crontab_time:
            _times = set()
            for t_str in crontab_time.split(','):
                t = self._get_int(t_str, replacement_map)
                _times.add(t)
            times = list(_times)
        else:
            t = self._get_int(crontab_time, replacement_map)
            times.append(t)

        times.sort()
        return times
