#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from crontab.modinfo import ModInfo
from crontab.store.crontab_o import CrontabO
from crontab.store.crontab_store import CrontabStore
from crontab.store.manage_crontab import ManageCrontab

from sims4communitylib.dialogs.common_choice_outcome import CommonChoiceOutcome
from sims4communitylib.dialogs.common_input_text_dialog import CommonInputTextDialog

from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand, CommonConsoleCommandArgument
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry


log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class CrontabUI:
    def __init__(self):
        pass

    @staticmethod
    def nop(*args):
        log.debug(f"Running nop '{args}'")  # default fall-back method

    def add_entry(self):
        def _on_submit(input_value: str, outcome: CommonChoiceOutcome):
            if outcome == CommonChoiceOutcome.CHOICE_MADE:
                mc = ManageCrontab()
                mc.add_crontab_line(input_value, save_data=False)

        title_tokens = ("Add 'crontab' Entry", )
        # "arg1, arg2, arg3, ..." "test1, test2, test3, ..." - TODO
        # WARNING: non-static methods require 1st parameter 'self'
        description_tokens = ("Format: 'MM HH WD S MP cmd arg1 arg2 ...'\nn - Single value\nn,o,... - Individual values\nn-o - Range\n"
                              "*/o - Every 'o'-th call\nn/o - Every 'o'-th call starting at n\n"
                              "Minutes (MM): 0-59; Hours (HH): 0-23\n"
                              "Weekdays (WD): 0-6 (or Su,Mo,Tu,We,Th,Fr,Sa)\n"
                              "Seasons (S): 0-3 (or Summer,Fall,Winter,Spring)\n"
                              "Moon phases (MP): 0-7 (or New_Moon,Waxing_Crecent,First_Quater,Waxing_Gibbous,Full_Moon,Waning_Gibbous,Third_Quarter,Waning_Crecent)\n")
        dialog = CommonInputTextDialog(
            ModInfo.get_identity(),
            0xFC089996,
            0xFC089996,
            initial_value="59 23 * * * command",
            title_tokens=title_tokens,
            description_tokens=description_tokens,
        )
        dialog.show(on_submit=_on_submit)

    @staticmethod
    @CommonConsoleCommand(
        ModInfo.get_identity(),
        'o19.crontab.show',
        "Usage: o19.crontab.show to list all crontab entries"
    )
    def o19_cmd_crontab_show(output: CommonConsoleCommandOutput):
        try:
            cs = CrontabStore()
            output(f"crontab_lines: {cs.crontab_lines}")
            output(f"cron_jobs: {cs.cron_jobs}")
            output(f"schedules: {cs.cron_job_schedules}")
            log.debug(f"crontab_lines: {cs.crontab_lines}")
            log.debug(f"cron_jobs: {cs.cron_jobs}")
            log.debug(f"schedules: {cs.cron_job_schedules}")
            output("ok")
        except Exception as e:
            output(f"Error: {e}")

    @staticmethod
    @CommonConsoleCommand(
        ModInfo.get_identity(),
        'o19.crontab.add_ui',
        "Usage: o19.crontab.add to show a dialog. Use 'o19.crontab.save' to save it.",
    )
    def o19_cmd_crontab_add_ui(output: CommonConsoleCommandOutput):
        try:
            cui = CrontabUI()
            cui.add_entry()
            output("ok")
        except Exception as e:
            output(f"Error: {e}")

    @staticmethod
    @CommonConsoleCommand(
        ModInfo.get_identity(),
        'o19.crontab.add',
        "Usage: o19.crontab.add 'crontab_line' to add a crontab entry. Use 'o19.crontab.save' to save it.",
        command_arguments=(
                CommonConsoleCommandArgument('crontab_line', 'str', 'Complete crontab line (* * * * * command).', is_optional=True),
        )
    )
    def o19_cmd_crontab_add(output: CommonConsoleCommandOutput, crontab_line: str):
        try:
            mc = ManageCrontab()
            job_id = mc.add_crontab_line(crontab_line, save_data=False)
            output(f"ok ({job_id})")
        except Exception as e:
            output(f"Error: {e}")

    @staticmethod
    @CommonConsoleCommand(
        ModInfo.get_identity(),
        'o19.crontab.save',
        'Usage: o19.crontab.save to save the crontab.',

    )
    def o19_cmd_crontab_save(output: CommonConsoleCommandOutput):
        try:
            co = CrontabO()
            co.save()
            output(f"ok")
        except Exception as e:
            output(f"Error: {e}")
