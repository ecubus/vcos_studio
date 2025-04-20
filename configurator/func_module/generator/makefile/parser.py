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

CUR_FILE_PATH = os.path.dirname(__file__)


def get_config_dict(sys_config: dict) -> dict:
    update_kfg_module_enabled_list(sys_config)


def update_kfg_module_enabled_list(sys_config):
    sys_config["modules_info"]["kfg_module_all_list"] = {}
    for module_name in sys_config["modules_info"]["enabled_module_list"]:
        if module_name == "Os":
            sys_config["modules_info"]["kfg_module_all_list"].update({"VCOS_MODULE_CONFIG_AUTOSAROS": "y"})
        else:
            sys_config["modules_info"]["kfg_module_all_list"].update({f"VCOS_MODULE_CONFIG_{module_name.upper()}": "y"})

    pass
