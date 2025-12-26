#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import time
from typing import List, Dict, Any

from crontab.modinfo import ModInfo
from crontab.store.crontab_store import CrontabStore
from ts4lib.utils.singleton import Singleton

from sims4communitylib.events.interval.common_interval_event_service import CommonIntervalEventRegistry
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

import services

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


try:
    from lunar_cycle.lunar_cycle_service import LunarCycleService
    from seasons.season_service import SeasonService
    from sims4communitylib.utils.common_time_utils import CommonTimeUtils
    from sims4communitylib.utils.time.common_alarm_utils import CommonAlarmUtils
except:
    pass


class Scheduler(object, metaclass=Singleton):
    """
    Class to actually process the crontab entries
    """

    t_last_run = -1
    date_and_time = -1

    profiling_enabled = True
    schedules: int = 0  # may store the number of runs
    duration: float = 0  # may store the exec time of the main method
    cron_job_execs_times: Dict[str, List] = dict()  # {'job_id': ['executions', 'duration'], ...}
    """ cron_job_execs_times may store the exec times """

    def __init__(self):
        Scheduler.t_last_run, _, _, _ = self._get_current_sim_time()
        # self._alarm_handle = None
        # self.start(granularity=1)

    def profiling(self, enable_profiling: bool = None) -> bool:
        """ En-/Disable profiling; use None to query the current settings """
        if enable_profiling is not None:
            Scheduler.profiling_enabled = enable_profiling
        return Scheduler.profiling_enabled

    @staticmethod
    def log_profiling_data():
        #  {'profiler': [2, 0.007950067520141602]}
        log.debug(f"Profiling data: TOTAL: [{Scheduler.schedules} runs, {Scheduler.duration:0.3f} s]")
        log.debug(f"Profiling data: {Scheduler.cron_job_execs_times}")

    @staticmethod
    def get_profiling_data():
        return Scheduler.schedules, Scheduler.duration, Scheduler.cron_job_execs_times

    @staticmethod
    def reset_profiling_data():
        Scheduler.schedules = 0
        Scheduler.duration = 0
        Scheduler.cron_job_execs_times = dict()

    def _get_current_sim_time(self):
        """
        :return: Current minute of the day (0-1439), weekday (0-7), season (0-3) and moon_phase (0-7)
        """
        try:
            ctu = CommonTimeUtils()
            date_and_time = ctu.get_current_date_and_time()
            hour = ctu.get_current_hour(date_and_time) % 24
            minute = ctu.get_current_minute(date_and_time) % 60
            weekday = ctu.get_day_of_week(date_and_time) % 7
            # log.debug(f"w {weekday}")
            try:
                # log.debug(f"s: {type(services.season_service().season)} = {int(services.season_service().season)}")
                season_service: SeasonService = services.season_service()
                season = int(season_service.season) % 4
            except:
                season = -1
            try:
                lunar_cycle_service: LunarCycleService = services.lunar_cycle_service()
                moon_phase = int(lunar_cycle_service.current_phase) % 8
            except:
                moon_phase = -1
            return hour * 60 + minute, weekday, season, moon_phase
        except Exception as e:
            log.error(f"Oops: '{e}'", throw=False)
            return 0, 0, 0, 0

    def _process_next_time(self):
        t_call = time.time()

        def _do_job(_t: int, _weekday: int, _season: int, _moon_phase: int):
            cs = CrontabStore()
            job_ids = cs.cron_job_schedules.get(_t, [])
            if not job_ids:
                return
            log.debug(f"Checking t={_t}, wd={_weekday}, s={_season}, mp={_moon_phase} --> '{job_ids}'")
            _job_queue: Dict[Any, List] = dict()
            for job_id in job_ids:
                function, arguments, weekdays, seasons, moon_phases = cs.cron_jobs.get(job_id)
                if (_weekday in weekdays) and (_season in seasons or _season == -1) and (_moon_phase in moon_phases or moon_phase == -1):
                    # Make sure to run every job only one time, no matter how big the time jump is (if any)
                    _job_queue.update({job_id: [function, arguments]})
            for job_id, (function, arguments) in _job_queue.items():
                t_job = time.time()
                # noinspection PyBroadException
                try:
                    log.debug(f"{function}({arguments})")
                    function(*arguments)
                except Exception as e:
                    log.warn(f"Error in '{function}({arguments})'")
                    log.error(f"{e}")
                if Scheduler.profiling_enabled:
                    dt_job = time.time() - t_job
                    executions, duration = Scheduler.cron_job_execs_times.get(job_id, [0, 0])
                    executions += 1
                    duration += dt_job
                    Scheduler.cron_job_execs_times.update({job_id: [executions, duration]})

        ctu = CommonTimeUtils()
        date_and_time = ctu.get_current_date_and_time()
        if date_and_time > Scheduler.date_and_time:
            Scheduler.date_and_time = date_and_time
        else:
            # Game time went backwards or is stalled: Do nothing
            return

        t_now, weekday, season, moon_phase = self._get_current_sim_time()  # t_now is 0..1439
        t_last_run = Scheduler.t_last_run

        if t_now > t_last_run:
            # execute all jobs between last_run and now
            for t in range(t_last_run + 1, t_now + 1):
                _do_job(t, weekday, season, moon_phase)
        elif t_now < t_last_run:
            # execute all jobs between last_run and now, after switch from 23:59 to 00:00 (or 23:57 to 0:04)
            for t in range(t_last_run + 1, 24 * 60):
                _do_job(t, weekday, season, moon_phase)
            for t in range(0, t_now + 1):
                _do_job(t, weekday, season, moon_phase)
        else:
            return  # should be handled by CommonTimeUtils above
        Scheduler.t_last_run = t_now

        if Scheduler.profiling_enabled:
            dt_call = time.time() - t_call
            Scheduler.schedules += 1
            Scheduler.duration += dt_call

    @staticmethod
    @CommonIntervalEventRegistry.run_every(ModInfo.get_identity(), milliseconds=1000)
    def o19_crontab_run_every_s():
        if CommonTimeUtils.game_is_paused():
            return
        Scheduler()._process_next_time()
