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
from PySide6 import QtWidgets
import os
from cfg_gui.rte_editor.task_mapping_ui import TaskMappingUI

CUR_FILE_PATH = os.path.dirname(__file__)
RTE_TAB_IDX: dict = {
    "Task Mapping": 0,
    "Port Mapping": 1,
    "Data Mapping": 2,
    "Service Mapping": 3,
}


class RteEditUI(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_mapping()

    def init_mapping(self):
        self.task_mapping_ui = TaskMappingUI()
        self.is_task_mapping_data_updated = False
