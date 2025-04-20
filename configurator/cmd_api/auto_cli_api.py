# This Python file uses the following encoding: utf-8
############################################################################
# Copyright (c) 2025 Li Auto Inc. and its affiliates
# Licensed under the Apache License, Version 2.0(the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################################################
import os
from cmd_adaptor.func_logic_layer.load_save_project import LoadAndSaveProject
from cmd_adaptor.func_logic_layer.import_func.import_asw_handler import ImportAswHandler
from cmd_adaptor.func_logic_layer.mapping_func.task_mapping_cmd_func import TaskMappingCmdFunc
from cmd_adaptor.func_logic_layer.generate_func.generate_cmd_func import GenerateCmdFunc
from cmd_adaptor.func_logic_layer.validation_func.validate_cmd_func import ValidateCmdFunc
from cmd_adaptor.func_logic_layer.export_func.export_file_func import ExportFileFunc
from cmd_adaptor.func_logic_layer.bsw_func.os_cmd_func import OsCmdFunc
from cmd_adaptor.func_logic_layer.os_cfg_cmd_func import OsConfigureCmdFunc
from cmd_adaptor.func_logic_layer.import_func.import_mcal_handler import ImportMcalHandler
from cmd_adaptor.func_logic_layer.mapping_func.schedule_table_mapping_cmd_func import ScheduleTableCmdFunc
from cmd_adaptor.cmd_interaction.cmd_logger import logger


class AutoCliApi:

    @classmethod
    def load_project(cls, project_file_path) -> bool:
        """load the vcos project by project file path, include all kinds of arxml and logs.

        Args:
            project_file_path (str): the .vcosproject file path.

        Returns:
            bool: True(load sucessfully), False:(load failed).
        """
        if not os.path.exists(project_file_path) or ".vcosproject" not in project_file_path:
            logger.error(f"project file path {project_file_path} format error")
            return False
        return LoadAndSaveProject.load_project(project_file_path)

    @classmethod
    def save_project(cls) -> bool:
        """save the project into arxml and logs.

        Returns:
            bool: True(save sucessfully), False:(save failed).
        """
        return LoadAndSaveProject.save_project_all_info()

    @classmethod
    def import_asw(cls, asw_dir: str) -> bool:
        """import the asw files according to the directory path.

        Args:
            asw_dir (str): the directory which store the asw arxmls.

        Returns:
            bool: True(import sucessfully), False:(import failed).
        """
        if not os.path.exists(asw_dir):
            logger.error(f"asw dir {asw_dir} not exists")
            return False
        return ImportAswHandler.import_asw(asw_dir)

    @classmethod
    def import_mcal(cls, mcal_path: str, mcal_module_list: list) -> bool:
        """import the mcal file path according to the mcal path.

        Args:
            mcal_path (str): the mcal file path.
            mcal_module_list (list): the MCAL modules that need to be imported

        Returns:
            bool: True(import sucessfully), False:(import failed).
        """
        if not isinstance(mcal_path, str) or not os.path.isfile(mcal_path):
            logger.error("mcal path is invalid, please check mcal path what you config!")
            return False
        if not mcal_module_list or not isinstance(mcal_module_list, list):
            logger.error("mcal module list is invalid, please check mcal module list what you want import")
            return False
        try:
            ImportMcalHandler.import_mcal_arxml(mcal_path, mcal_module_list)
        except Exception:
            return False
        return True

    @classmethod
    def excute_task_mapping(cls, task_mapping_info_list: list) -> bool:
        """excute the task mapping by the list of task mapping info

        Args:
            task_mapping_info_list (list): the list of task_mapping_info
            (the dict of containing the below task mapping params).
                task_name (str): the task name which to be mapped.
                swc_name (str): the swc name which the runnable belongs to.
                runnable_name (str): the runnable or main function name.
                position (int): the target position of task, (-1:default to the last unused position,
                                > 0: the target position).
                event_name (str): If the runnable_name has multiple different runnables,
                                this parameter must be specified.

        Returns:
            bool: True(excute sucessfully), False:(excute failed)

        Note:
            only support Application Components
        """
        for task_mapping_info in task_mapping_info_list:
            task_name = task_mapping_info.get("task_name")
            swc_name = task_mapping_info.get("swc_name")
            runnable_name = task_mapping_info.get("runnable_name")
            position = task_mapping_info.get("position")
            event_name = task_mapping_info.get("event_name", "")
            result = TaskMappingCmdFunc.auto_task_mapping_by_param(
                task_name, swc_name, runnable_name, position, event_name
            )
            if not result:
                return False

        return True

    @classmethod
    def excute_task_mapping_by_file(cls, excel_file: str) -> bool:
        """excute the task mapping by the input excel file

        Args:
            excel_file (str): excel path

        Returns:
            bool: True(excute sucessfully), False:(excute failed)
        """
        if not os.path.exists(excel_file):
            logger.error(f"excel file {excel_file} not exists")
            return False
        return TaskMappingCmdFunc.auto_task_mapping_by_file(excel_file)

    @classmethod
    def excute_validation(cls, validation_module_list: list, validation_level: str) -> dict:
        """excute the validation by the list of module and validation level.

        Args:
            validation_module_list (list): the list of the module needed to be validated.

            validation_level (str): "no limit"(only ouput the important rules),
                                    "error"(output the important rules and error result),
                                    "warnning"(output the important rules、error and warning result).

        Returns:
            validation_dict: the validation result dict, key:module_name, value:True/False.
            validation_logs: Detailed error and warning validation items.
        """
        if validation_level and validation_level not in ["no limit", "error", "warnning"]:
            logger.error(f"validation_level {validation_level} value error")
            return False
        validation_dict, validation_logs = ValidateCmdFunc.validate_modules_with_result(
            validation_module_list, validation_level
        )
        return validation_dict, validation_logs

    @classmethod
    def excute_generation(
        cls, generation_module_list: list, is_debug: bool = False, forced_codegen: bool = True
    ) -> dict:
        """excute the generation by the list of module.

        Args:
            generation_module_list (list): the list of the module needed to be generated.

            is_debug (bool) : optional param, generate mode(debug or release), default value(release)

            forced_codegen (bool) : optional param, all-generate or add-generate mode, default value(all-generate mode)

        Returns:
            dict: the generation result dict, key:module_name, value:True/False.
        """
        result = GenerateCmdFunc.execute_auto_generate(generation_module_list, is_debug, forced_codegen)
        return result

    @classmethod
    def export_task_mapping(cls, file_path) -> bool:
        """export the task mapping result into one excel file.

        Returns:
            bool: True(excute sucessfully), False:(excute failed).
        """

        return ExportFileFunc.export_task_mapping_info_to_excel(file_path)

    @classmethod
    def add_spinlock(cls, spinlock_info: dict) -> bool:
        """add/update a spinlock by spinlock_info

        Args:
            spinlock_info (dict): the dict of containing the below spinlock params.

                spinlock_id (str): the unique name of a spinlock

                spinlock_method (str): the method should in (LOCK_ALL_INTERRUPTS/LOCK_CAT2_INTERRUPTS/LOCK_NOTHING)

                app_name_list (str): the param for OsSpinlockAccessingApplication,
                                    and the app name should be unique and the count should >= 2

        Returns:
            bool: True(excute sucessfully), False:(excute failed)
        """
        if "spinlock_id" not in spinlock_info:
            logger.error("spinlock_info should contain spinlock_id")
            return False
        if "spinlock_method" not in spinlock_info:
            logger.error("spinlock_info should contain spinlock_method")
            return False
        if "app_name_list" not in spinlock_info:
            logger.error("spinlock_info should contain app_name_list")
            return False
        return OsCmdFunc.add_spinlock(spinlock_info)

    @classmethod
    def remove_spinlock(cls, spinlock_id: str) -> bool:
        """remove a spinlock by spinlock_id

        Args:
            spinlock_id (str): the unique name of a spinlock

        Returns:
            bool: True(excute sucessfully), False:(excute failed)
        """
        if not spinlock_id:
            logger.error("spinlock_id is empty")
            return False
        return OsCmdFunc.remove_spinlock(spinlock_id)

    @classmethod
    def import_os_cfg(cls, file_name: str) -> bool:
        """在指定工程中导入OS自动配置
        Args:
            file_name(str): name of file to import
        Returns:
            bool: True(import sucessfully), False:(import failed)
        """
        if not os.path.exists(file_name):
            logger.error(f"os cfg file {file_name} not exists")
            return False
        return OsConfigureCmdFunc.import_os_cfg(file_name)

    @classmethod
    def export_os_cfg(cls, file_name: str) -> bool:
        """导出指定工程现有OS配置
        Args:
            file_name(str): name of file to export
        Returns:
            bool: True(export sucessfully), False:(export failed)
        """
        return OsConfigureCmdFunc.export_os_cfg(file_name)

    @classmethod
    def generate_all_schedule_table(cls):
        """
        生成所有的调度表配置
        Returns:
            bool: True(generate sucessfully), False:(generate failed)
        """
        res = ScheduleTableCmdFunc.generate_schedule_table_cfg()
        if not res:
            logger.error("generate schedule table cfg failed")
            return False
        task_mapping_instance = TaskMappingCmdFunc.get_task_mapping_instance()
        task_mapping_instance.update_schedule_table_info()
        logger.info("generate schedule table cfg success")
        return True
