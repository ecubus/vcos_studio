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
from ui_adaptor.data_management import data_management as data
from func_module.module_management.arxml_handler.arxml_parse_save import ArxmlParseHandler
from func_module.project_management.sys_info_class import SysInfoClass
from basic_func_module.autosar_utils.autosar_util import AutosarUtil
from basic_func_module.autosar_utils.autosar_utils import AutosarUtils
from basic_func_module.base_logger import logger
from basic_func_module.autosar_utils.utils import get_short_name, get_definition_ref
from func_module.health_monitor import perf_record
from func_module.module_management.arxml_handler.mcal_ecuc.import_ecuc_cfg import EcucCfgImport


class ImportFilesLogic:

    def __init__(self) -> None:
        pass

    def judge_file_is_asw_arxml(self, file_obj: object) -> bool:
        """判断一个文件是否为 asw 文件"""
        SWC_DATA_TYPE_PORT_INTERFACE = [
            "DATA-TYPE-MAPPING-SET",
            "APPLICATION-PRIMITIVE-DATA-TYPE",
            "APPLICATION-ARRAY-DATA-TYPE",
            "DATA-TYPE-MAP",
            "APPLICATION-ARRAY-ELEMENT",
            "ARRAY-SIZE-HANDLING-ENUM",
            "APPLICATION-RECORD-DATA-TYPE",
            "CLIENT-SERVER-INTERFACE",
            "APPLICATION-RECORD-ELEMENT",
            "VARIABLE-DATA-PROTOTYPE",
            "PARAMETER-INTERFACE",
            "PARAMETER-DATA-PROTOTYPE",
            "SENDER-RECEIVER-INTERFACE",
            "MODE-SWITCH-INTERFACE",
            "NV-DATA-INTERFACE" "TRIGGER-INTERFACE-MAPPING",
            "PORT-INTERFACE-MAPPING-SET",
            "CLIENT-SERVER-INTERFACE-MAPPING",
        ]
        ILLEGAL_KEY_WORD = [
            "BSW-MODULE-DESCRIPTION",
            "SERVICE-SW-COMPONENT-TYPE",
            "ECUC-MODULE-CONFIGURATION-VALUES",
            "DATA-MAPPINGS",
            "I-SIGNAL-I-PDU",
        ]
        # 1. 存在 asw 的字段
        for asw_key_word in AutosarUtils.SUPPORT_APPL_COMPONENT_TYPE:
            if len(AutosarUtil.find_nodes(file_obj, asw_key_word, True)) > 0:
                return True
        # 2. 过滤 ib, service component, ecuc, flatExtract, communication arxml
        for illegal_key_word in ILLEGAL_KEY_WORD:
            if len(AutosarUtil.find_nodes(file_obj, illegal_key_word, True)) > 0:
                return False
        # 有 SWComponentTemplate::dataType 内或者 interface 的字段也认为是asw文件
        for key_word in SWC_DATA_TYPE_PORT_INTERFACE:
            if len(AutosarUtil.find_nodes(file_obj, key_word, True)) > 0:
                return True
        return False

    def judge_file_is_ecuc_arxml(self, file_obj: object):
        """判断一个文件是否为 ecuc arxml"""
        if len(AutosarUtil.find_nodes(file_obj, "ECUC-MODULE-CONFIGURATION-VALUES", True)) > 0:
            return bool(get_short_name(file_obj.AR_PACKAGES.AR_PACKAGE[0]) != "InitialEcuC")

        return False

    @perf_record.log_function_stats(["BSW Editor", "配置文件解析和导入", "ASW arxml导入"])
    def apply_asw_import(self, dir_path, progress_signal):
        if len(dir_path) == 0:
            return
        arxml_files = AutosarUtil.get_arxml_file_from_path(dir_path)
        # 拦截非 asw arxml 文件，并提示
        illegal_files = []
        with AutosarUtil.gc_guard():
            for file_path in arxml_files:
                progress_signal.emit(f"validate {os.path.basename(file_path)} is legal to import...")
                if not self.judge_file_is_asw_arxml(AutosarUtil.parse_arxml(file_path)):
                    illegal_files.append(file_path)
                AutosarUtil.trigger_gc()
        for illegal_file_path in illegal_files:
            arxml_files.remove(illegal_file_path)

        if len(arxml_files) > 0:
            progress_signal.emit("Importing asw...")
        self.apply_asw_import_by_select_files(arxml_files)

        return illegal_files

    def apply_asw_import_by_select_files(self, file_list: list):
        if len(file_list) == 0:
            return
        sys_info_obj: SysInfoClass = data.sys_info_class
        sys_info_obj.swc = os.path.dirname(file_list[0])
        res, component_arxml_path_dict_info = ArxmlParseHandler.asw_arxml_merge_logic(
            file_list, sys_info_obj.config_base_path
        )
        if "asw" not in res:
            logger.warning("Cannot get asw info")
        else:
            data.autosar_asw_class = res["asw"]

        data.component_arxml_path_dict = {"asw_component": component_arxml_path_dict_info}

    def get_all_module_of_mcal_arxml(self, file_path):
        # 1. 解析mcal文件
        if file_path is None:
            logger.ui_warning("You did not select the mcal arxml file, please select.")
            return None
        parse_res = ArxmlParseHandler.parse_mcal_arxml(file_path)
        return self.get_mcal_list_prefix(parse_res, file_path)

    def get_mcal_list_prefix(self, parse_res, file_path):
        supported_mcal_module_list = []
        sys_info_obj: SysInfoClass = data.sys_info_class
        all_ecuc_objs = parse_res.find_nodes("ECUC-MODULE-CONFIGURATION-VALUES")

        mcal_arxml_dict = {}
        for module_obj in all_ecuc_objs:
            module_name = get_short_name(module_obj)
            mcal_arxml_dict[module_name] = AutosarUtil.to_ecuc_module_configuration_values_dict(module_obj)

        prefix = get_definition_ref(all_ecuc_objs[0]).split("/")[1]

        data.cfg_info_dict["eb"] = {"arxml": mcal_arxml_dict}
        # 2. 更新mcal的导入信息到sys_info_obj
        data.sys_info_class.eb_arxml = file_path
        all_modules_of_mcal_list = [get_short_name(ecuc_obj) for ecuc_obj in all_ecuc_objs]

        for module_name in all_modules_of_mcal_list:
            if ArxmlParseHandler.check_mod_files_exist(sys_info_obj.plug_in_bswmd_path, [module_name]):
                supported_mcal_module_list.append(module_name)

        return supported_mcal_module_list, prefix

    @perf_record.log_function_stats(["BSW Editor", "配置文件解析和导入", "Ecuc和ASW arxml文件", "Ecuc和ASW arxml导入"])
    def import_all_types_arxml(self, need_update_ecuc_dcit, asw_file_list: list = None, progress_signal=None):
        # 更新 ecuc
        prefix_diff_modules = {}
        if need_update_ecuc_dcit is not None and len(need_update_ecuc_dcit) > 0:
            progress_signal.emit("Updating ecuc module information...")
            prefix_diff_modules = EcucCfgImport.update_ecuc_autosar_dict(data, need_update_ecuc_dcit)

        # 最后更新 asw
        if asw_file_list is not None and len(asw_file_list) > 0:
            progress_signal.emit("Updating asw information...")
            self.apply_asw_import_by_select_files(asw_file_list)

        return data.autosar_bswmd_class, data.autosar_bsw_class, prefix_diff_modules
