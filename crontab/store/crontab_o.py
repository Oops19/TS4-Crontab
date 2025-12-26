#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import os

from crontab.modinfo import ModInfo
from crontab.store.crontab_store import CrontabStore
from ts4lib.libraries.ts4folders import TS4Folders

from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class CrontabO:
    def __init__(self):
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)

    def save(self):
        file_name = os.path.join(self.ts4f.data_folder, 'crontab.txt')
        try:
            cs = CrontabStore()
            with open(os.path.join(self.ts4f.data_folder, 'crontab.txt'), 'wt', encoding='UTF-8') as fp:
                for job_id, crontab in cs.crontab_lines.items():
                    fp.write(f"{crontab}  # {job_id}\r\n")
        except Exception as e:
            log.error(f"Couldn't write {file_name}")