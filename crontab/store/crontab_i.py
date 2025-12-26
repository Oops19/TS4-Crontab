#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import os

from crontab.modinfo import ModInfo
from crontab.store.manage_crontab import ManageCrontab
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
from ts4lib.libraries.ts4folders import TS4Folders

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class CrontabI:
    def __init__(self):
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)

    def load(self):
        file_name = os.path.join(self.ts4f.data_folder, 'crontab.txt')
        try:
            mc = ManageCrontab()
            with open(file_name, 'rt', encoding='UTF-8') as fp:
                data = fp.read()
                for line in data.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    mc.add_crontab_line(line, save_data=False)
        except Exception as e:
            log.error(f"Couldn't import {file_name}")