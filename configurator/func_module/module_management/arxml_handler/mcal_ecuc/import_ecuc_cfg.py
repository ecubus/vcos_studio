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
from basic_func_module.base_logger import logger
from basic_func_module.autosar_utils.autosar_ecuc import AutosarEcuc
from basic_func_module.autosar_utils.autosar_util import AutosarUtil
from func_module.module_management.arxml_handler.arxml_parse_save import ArxmlParseHandler
from func_module.module_management.module_management import ModuleManagement


class EcucCfgImport:

    @classmethod
    def module_can_be_imported(cls, ecuc_module_info, autosar_mod_class, prefix_diff_modules, module_name, file_path):
        """checks whether the module can be imported and saves its info"""

        ecuc_module_obj = ecuc_module_info["ecuc_module_obj"]
        force_import = ecuc_module_info.get("force_import", False)
        ecuc_prefix = ArxmlParseHandler.get_ecuc_module_preifx(ecuc_module_obj)
        mod_prefix = ArxmlParseHandler.get_mod_perfix(module_name, autosar_mod_class)
        can_be_imported = True

        if mod_prefix is not None and ecuc_prefix != mod_prefix and not force_import:
            logger.ui_error(f"The chips in the project differ from the {module_name} in ARXML, causing import failure.")
            can_be_imported = False
            if file_path not in prefix_diff_modules:
                prefix_diff_modules[file_path] = {}
            prefix_diff_modules[file_path][module_name] = {"ecuc_module_obj": ecuc_module_obj, "force_import": False}

        return can_be_imported, ecuc_prefix

    @classmethod
    def update_ecuc_autosar_dict(cls, data, need_update_ecuc_dcit: dict):
        module_manage = ModuleManagement(
            data.sys_info_class, data.autosar_bsw_class, data.autosar_bswmd_class, data.autosar_ib_class
        )
        module_cfg = getattr(data, "sys_target_dict", {}).get("module_cfg", {})
        selected_mcal_modules_list = []
        mcal_prefix_dict = {}
        data.cfg_info_dict["eb"] = {"arxml": {}}
        prefix_diff_modules = {}

        for file_path, ecuc_module_dict in need_update_ecuc_dcit.items():
            for module_name, module_info in ecuc_module_dict.items():
                ecuc_obj = module_info["ecuc_module_obj"]
                # parse base ecuc for mcal modules
                if module_cfg.get(module_name, {}).get("is_mcal"):
                    # save eb file path
                    data.sys_info_class.eb_arxml = file_path
                    can_import, ecuc_prefix = cls.module_can_be_imported(
                        module_info, data.autosar_bswmd_class, prefix_diff_modules, module_name, file_path
                    )
                    if not can_import:
                        continue
                    mcal_prefix_dict[module_name] = ecuc_prefix
                    ecuc_cfg_obj_list = module_info["ecuc_module_obj"].find_nodes("ECUC-MODULE-CONFIGURATION-VALUES")
                    if not ecuc_cfg_obj_list:
                        continue
                    selected_mcal_modules_list.append(module_name)
                    data.cfg_info_dict["eb"]["arxml"][module_name] = (
                        AutosarUtil.to_ecuc_module_configuration_values_dict(ecuc_cfg_obj_list[0])
                    )
                    if module_name in data.sys_info_class.enable_modules:
                        continue
                    # bswmd must be loaded before updating base ecuc
                    if module_name not in data.autosar_bswmd_class:
                        data.autosar_bswmd_class.update(
                            ArxmlParseHandler.parse_all_bswmd_arxml(
                                data.sys_info_class.plug_in_bswmd_path, [module_name], data.sys_info_class.target
                            )
                        )
                    # update ecuc module info by base ecuc
                    ecuc_obj = module_manage.load_ecuc(module_name, module_name, ecuc_prefix)
                    AutosarEcuc.record_default_file(
                        ecuc_obj.find(f"/ActiveEcuC/{module_name}"), f"{module_name}_ecuc.arxml"
                    )

                module_manage.update_ecuc_module_by_import(module_name, ecuc_obj)

        return prefix_diff_modules
