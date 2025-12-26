from crontab.modinfo import ModInfo
from crontab.scheduler import Scheduler
from crontab.store.crontab_i import CrontabI

from crontab.store.crontab_store import CrontabStore
from crontab.store.manage_crontab import ManageCrontab
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


# class to load the crontab entries and to start the scheduler


class Main:
    @staticmethod
    @CommonEventRegistry.handle_events(ModInfo.get_identity())
    def handle_event(event_data: S4CLZoneLateLoadEvent):
        cs = CrontabStore()
        if not cs.is_initialized:
            log.debug(f"Starting {ModInfo.get_identity().name}")
            CrontabI().load()
            ManageCrontab().add_job("0 * * * *", "crontab.scheduler.Scheduler.log_profiling_data", job_id="profiler", save_data=False)
            Scheduler()
            cs.is_initialized = True


