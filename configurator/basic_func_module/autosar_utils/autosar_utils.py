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
from enum import Enum
from collections import deque
from basic_func_module.autosar_utils import utils
from basic_func_module.base_logger import logger
from func_module.health_monitor.perf_record import log_function_stats


class MemmapCategory(Enum):
    OSA_PRIVATE = "OSA_PRIVATE"
    OSA_SHARED = "OSA_SHARED"
    CORE_SHARED = "SHARED_CORE"
    GLOBAL = "GLOBAL"

    def __lt__(self, other):
        if not isinstance(other, MemmapCategory):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other):
        return hasattr(self, "value") and hasattr(other, "value") and self.value == other.value

    def __hash__(self):
        return hash(self.value)


class VariableInitCategory(Enum):
    NO_INIT = "NO_INIT"
    ZERO_INIT = "ZERO_INIT"
    INIT = "INIT"  # non-zero init values


def topological_sort(dependencies):

    def visit(node, visited, stack):
        visited.add(node)
        if node in dependencies:
            for dependency in dependencies[node]:
                if dependency not in visited:
                    visit(dependency, visited, stack)
        stack.append(node)

    visited, stack = set(), deque()
    for node in sorted(dependencies):
        if node not in visited:
            visit(node, visited, stack)

    return list(stack)


class AutosarUtils:
    __rte_codegen_dict = {}
    __last_task_mapping_info = {}
    __last_data_mapping_info = {}

    is_debug = False
    asw_dict_func_times = {}

    cal_prm_rport_type = "CAL_PRM_RPORT"

    @classmethod
    def get_last_rte_codegen_dict(cls):
        return cls.__rte_codegen_dict

    @classmethod
    def get_last_task_mapping_info(cls):
        return cls.__last_task_mapping_info

    @classmethod
    def get_last_data_mapping_info(cls):
        return cls.__last_data_mapping_info

    @classmethod
    @log_function_stats(["RTE", "RTE信息推理"])
    def get_rte_codegen_dict(cls, asw_autosar_dict, task_mappings_info, cfg_dict, parse_new_dict=True):
        if (parse_new_dict) or (not cls.__rte_codegen_dict):
            if ("asw" not in asw_autosar_dict) or (asw_autosar_dict["asw"] is None):
                return {}
            cls.__last_task_mapping_info = task_mappings_info
        else:
            cfg_dict["rte"]["data_mapping_config"] = cls.__last_data_mapping_info
        return cls.__rte_codegen_dict

    NATIVE_DATATYPES = [
        "boolean",
        "float32",
        "float64",
        "uint8",
        "uint8_least",
        "sint8",
        "sint8_least",
        "uint16",
        "uint16_least",
        "sint16",
        "sint16_least",
        "uint32",
        "uint32_least",
        "sint32",
        "sint32_least",
        "uint64",
        "uint64_least",
        "sint64",
        "sint64_least",
        "void",
    ]
    AUTOMIC_DATATYPES = [
        "boolean",
        "float32",
        "uint8",
        "uint8_least",
        "sint8",
        "sint8_least",
        "uint16",
        "uint16_least",
        "sint16",
        "sint16_least",
        "uint32",
        "uint32_least",
        "sint32",
        "sint32_least",
    ]

    # NOTICE: compiler dependent
    NATIVE_DATATYPES_SIZE = {
        # short name
        "boolean": 1,
        "bool": 1,
        "uint8": 1,
        "sint8": 1,
        "uint16": 2,
        "sint16": 2,
        "uint32": 4,
        "sint32": 4,
        "uint64": 8,
        "sint64": 8,
        "float32": 4,
        "float64": 8,
        "uint8_least": 4,
        "sint8_least": 4,
        "uint16_least": 4,
        "sint16_least": 4,
        "uint32_least": 4,
        "sint32_least": 4,
        # native c
        "unsigned char": 1,
        "signed char": 1,
        "unsigned short": 2,
        "signed short": 2,
        "unsigned int": 4,
        "signed int": 4,
        "float": 4,
        "unsigned long long": 8,
        "signed long long": 8,
        "double": 8,
    }

    EVENT_TYPE = {
        "INIT-EVENT": "InitEvent",
        "TIMING-EVENT": "TimingEvent",
        "BACKGROUND-EVENT": "BackgroundEvent",
        "DATA-RECEIVED-EVENT": "DataReceivedEvent",
        "OPERATION-INVOKED-EVENT": "OperationInvokedEvent",
        "SWC-MODE-SWITCH-EVENT": "SwcModeSwitchEvent",
        "MODE-SWITCHED-ACK-EVENT": "ModeSwitchedAckEvent",
        "DATA-SEND-COMPLETED-EVENT": "DataSendCompletedEvent",
        "DATA-WRITE-COMPLETED-EVENT": "DataWriteCompletedEvent",
        "ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT": "AsynchronousServerCallReturnsEvent",
        "INTERNAL-TRIGGER-OCCURRED-EVENT": "InternalTriggerOccurredEvent",
        "EXTERNAL-TRIGGER-OCCURRED-EVENT": "ExternalTriggerOccurredEvent",
    }

    RUNNABLE_EVENT_TYPE = {
        "DATA-RECEIVED-EVENT": "DataReceivedEvent",
        "OPERATION-INVOKED-EVENT": "OperationInvokedEvent",
        "DATA-SEND-COMPLETED-EVENT": "DataSendCompletedEvent",
        "DATA-WRITE-COMPLETED-EVENT": "DataWriteCompletedEvent",
        "INTERNAL-TRIGGER-OCCURRED-EVENT": "InternalTriggerOccurredEvent",
        "EXTERNAL-TRIGGER-OCCURRED-EVENT": "ExternalTriggerOccurredEvent",
    }

    SUPPORT_APPL_COMPONENT_TYPE = [
        "APPLICATION-SW-COMPONENT-TYPE",
        "ECU-ABSTRACTION-SW-COMPONENT-TYPE",
        "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
        "NV-BLOCK-SW-COMPONENT-TYPE",
        "PARAMETER-SW-COMPONENT-TYPE",
        "SENSOR-ACTUATOR-SW-COMPONENT-TYPE",
        "SERVICE-PROXY-SW-COMPONENT-TYPE",
    ]

    GEN_FILE_APPL_COMPONENT_TYPE = [
        "APPLICATION-SW-COMPONENT-TYPE",
        "ECU-ABSTRACTION-SW-COMPONENT-TYPE",
        "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
        "SENSOR-ACTUATOR-SW-COMPONENT-TYPE",
        "SERVICE-PROXY-SW-COMPONENT-TYPE",
    ]

    # "NV-BLOCK-SW-COMPONENT-TYPE", "PARAMETER-SW-COMPONENT-TYPE"
    # 这两类不生成rte_swc_memmap.h/rte_swc.h/rte_swc_type.h/swc.c
    NO_GEN_FILE_APPL_COMPONENT_TYPE = list(set(SUPPORT_APPL_COMPONENT_TYPE) - set(GEN_FILE_APPL_COMPONENT_TYPE))

    SUPPORT_SERVICE_COMPONENT_TYPE = ["SERVICE-SW-COMPONENT-TYPE"]

    # 所有的component type
    SUPPORT_COMPONENT_TYPE = []
    SUPPORT_COMPONENT_TYPE.extend(SUPPORT_APPL_COMPONENT_TYPE)
    SUPPORT_COMPONENT_TYPE.extend(SUPPORT_SERVICE_COMPONENT_TYPE)

    GEN_FILE_COMPONENT_TYPE = []
    GEN_FILE_COMPONENT_TYPE.extend(GEN_FILE_APPL_COMPONENT_TYPE)
    GEN_FILE_COMPONENT_TYPE.extend(SUPPORT_SERVICE_COMPONENT_TYPE)

    datatype_mapping_sets = None
    adt_mappings = None
    idts = {}
    idts_dependency = None
    consts = None
    constraints = {}
    sw_component_types = None
    task_mappings = None
    asw_events = {}
    runnable_tasks = {}
    runnable_events = {}
    port_events = {}
    port_data_element_access = None
    port_operation_access = None
    operation_access = None
    run_operation_map = {}
    component_osapplications = None
    mapped_schedulable_entitys = None
    component_core_id = None
    pport_api_options = None
    # TODO: remove
    p_port_connection = None
    r_port_connection = None
    mode_groups = None
    datatype_path_to_idt_mapping = {}
    const_to_datatype_mapping = {}
    port_prototypes = None
    sr_p_port_path_to_asw_port_dict = {}
    sr_r_port_path_to_asw_port_dict = {}
    mode_r_port_path_to_asw_port_dict = {}
    p_connections = {}
    r_connections = {}
    is_ea_opt_enabled = False
    is_datamapping_opt_tx = False
    is_datamapping_opt_rx_1_1 = False
    is_datamapping_opt_rx_1_n = False
    sr_dm_glob_vars = {}
    server_runnable_connections = {}
    cs_ret_evt_trig_run = {}
    const_init_value = {}
    p_access_comspec_map = {}
    r_access_comspec_map = {}
    r_param_comspec_map = {}
    all_osa = []
    all_osa_set = set()
    core_osa_map = {}
    iso_call_func = {}
    iso_call_func_include_header_file = {}

    @classmethod
    def get_ecuc_partition_info(cls):
        ecuc_partition_osa = {}
        swc_osa_from_ep = {}
        swc_core_id_from_ep = {}
        swc_ecuc_partition = {}
        return ecuc_partition_osa, swc_osa_from_ep, swc_core_id_from_ep, swc_ecuc_partition

    @classmethod
    def get_all_sw_component_prototypes(cls, ar_asw):
        # 获取sw-component-type和sw-component-prototype的对应关系
        # 当前只支持实例化一个swc
        all_swc_prototypes = {}
        for component in ar_asw.find_nodes("COMPONENTS"):
            for swc_prototye in component.SW_COMPONENT_PROTOTYPE:
                swc_name = utils.get_valueOf(swc_prototye.SHORT_NAME)  # 实例化的swc名字
                base_swc_name = utils.get_valueOf(swc_prototye.TYPE_TREF).split("/")[-1]
                if base_swc_name not in all_swc_prototypes:
                    all_swc_prototypes.update({base_swc_name: []})
                    all_swc_prototypes[base_swc_name].append(swc_name)
                else:
                    all_swc_prototypes[base_swc_name].append(swc_name)
        return all_swc_prototypes

    @classmethod
    def get_all_appl_component_short_names(cls, ar_asw):
        if not ar_asw:
            return []
        name_list = set()
        sw_component_types = []
        # 只生成GEN_FILE_APPL_COMPONENT_TYPE这部分SWC列表
        for comp_type in cls.GEN_FILE_APPL_COMPONENT_TYPE:
            sw_component_types += ar_asw.find_nodes(comp_type)

        for swc_t in sw_component_types:
            name_list.add(utils.get_short_name(swc_t))
        return list(name_list)

    @classmethod
    def parse_datatype_mapping_sets_for_validation(cls, ar_asw):
        mapping_sets = {}
        adt_mappings = {}
        for mapping_set in ar_asw.find_nodes("DATA-TYPE-MAPPING-SET"):
            if mapping_set.DATA_TYPE_MAPS:
                mapping_set_path = mapping_set.get_path()
                mapping_sets[mapping_set_path] = {}
                for mapping in mapping_set.DATA_TYPE_MAPS.DATA_TYPE_MAP:
                    mapping_sets[mapping_set_path].update(
                        {
                            utils.get_valueOf(mapping.APPLICATION_DATA_TYPE_REF): utils.get_valueOf(
                                mapping.IMPLEMENTATION_DATA_TYPE_REF
                            )
                        }
                    )
                    adt_mappings.update(
                        {
                            utils.get_valueOf(mapping.APPLICATION_DATA_TYPE_REF): utils.get_valueOf(
                                mapping.IMPLEMENTATION_DATA_TYPE_REF
                            )
                        }
                    )
        return mapping_sets, adt_mappings

    @classmethod
    def get_all_ref_configuration_items_by_ref_target(cls, ecuc_autosar_dict, ref_target, new_ref_target=None):
        all_ref_configuration_items_by_ref_target_dict = {}
        for module_name, module_object in ecuc_autosar_dict.items():
            reference_object = module_object.find("/ActiveEcuC/" + module_name)
            if reference_object is None:
                continue
            containers = reference_object.CONTAINERS.parent_object_.CONTAINERS.ECUC_CONTAINER_VALUE
            for i in range(len(containers)):
                container = containers[i]
                if hasattr(container, "REFERENCE_VALUES") and container.REFERENCE_VALUES:
                    cls.traversal_ref_values(
                        container.REFERENCE_VALUES,
                        ref_target,
                        all_ref_configuration_items_by_ref_target_dict,
                        new_ref_target,
                    )
                cls.traversal_sub_container(
                    container, ref_target, all_ref_configuration_items_by_ref_target_dict, new_ref_target
                )

        return all_ref_configuration_items_by_ref_target_dict

    @classmethod
    def traversal_sub_container(
        cls, containers, ref_target, all_ref_configuration_items_by_ref_target_dict, new_ref_target=None
    ):

        sub_containers = containers.SUB_CONTAINERS
        if sub_containers:
            for i in range(len(sub_containers.ECUC_CONTAINER_VALUE)):
                sub_container = sub_containers.ECUC_CONTAINER_VALUE[i]
                if hasattr(sub_container, "REFERENCE_VALUES") and sub_container.REFERENCE_VALUES:
                    cls.traversal_ref_values(
                        sub_container.REFERENCE_VALUES,
                        ref_target,
                        all_ref_configuration_items_by_ref_target_dict,
                        new_ref_target,
                    )
                cls.traversal_sub_container(
                    sub_container, ref_target, all_ref_configuration_items_by_ref_target_dict, new_ref_target
                )

    @classmethod
    def traversal_ref_values(
        cls, ref_obj, ref_target, all_ref_configuration_items_by_ref_target_dict, new_ref_target=None
    ):
        if hasattr(ref_obj, "ECUC_INSTANCE_REFERENCE_VALUE") and ref_obj.ECUC_INSTANCE_REFERENCE_VALUE:
            for i in range(len(ref_obj.ECUC_INSTANCE_REFERENCE_VALUE)):
                if hasattr(ref_obj.ECUC_INSTANCE_REFERENCE_VALUE[i], "VALUE_IREF"):
                    ref_target_value = utils.get_value_iref(ref_obj.ECUC_INSTANCE_REFERENCE_VALUE[i])
                    if ref_target_value == ref_target:
                        emement = (
                            ref_obj.get_path()
                            + "/"
                            + ref_obj.ECUC_INSTANCE_REFERENCE_VALUE[i].DEFINITION_REF.valueOf_.split("/")[-1]
                        )
                        all_ref_configuration_items_by_ref_target_dict[emement] = ref_target_value
                        if new_ref_target:
                            utils.set_value_ref(ref_obj.ECUC_REFERENCE_VALUE[i], new_ref_target)
        if hasattr(ref_obj, "ECUC_REFERENCE_VALUE") and ref_obj.ECUC_REFERENCE_VALUE:
            for i in range(len(ref_obj.ECUC_REFERENCE_VALUE)):
                if hasattr(ref_obj.ECUC_REFERENCE_VALUE[i], "VALUE_REF"):
                    ref_target_value = utils.get_value_ref(ref_obj.ECUC_REFERENCE_VALUE[i])
                    if ref_target_value == ref_target:
                        emement = (
                            ref_obj.get_path()
                            + "/"
                            + ref_obj.ECUC_REFERENCE_VALUE[i].DEFINITION_REF.valueOf_.split("/")[-1]
                        )
                        all_ref_configuration_items_by_ref_target_dict[emement] = ref_target_value
                        if new_ref_target:
                            utils.set_value_ref(ref_obj.ECUC_REFERENCE_VALUE[i], new_ref_target)

    @classmethod
    def traversal_para_values_global_filter(cls, para_obj, all_element_items_list, filter_text=None):

        if hasattr(para_obj, "ECUC_ADD_INFO_PARAM_VALUE") and para_obj.ECUC_ADD_INFO_PARAM_VALUE:
            for i in range(len(para_obj.ECUC_ADD_INFO_PARAM_VALUE)):
                cls.get_para_element(para_obj.ECUC_ADD_INFO_PARAM_VALUE[i], all_element_items_list, filter_text)

        if hasattr(para_obj, "ECUC_NUMERICAL_PARAM_VALUE") and para_obj.ECUC_NUMERICAL_PARAM_VALUE:
            for i in range(len(para_obj.ECUC_NUMERICAL_PARAM_VALUE)):
                cls.get_para_element(para_obj.ECUC_NUMERICAL_PARAM_VALUE[i], all_element_items_list, filter_text)

        if hasattr(para_obj, "ECUC_TEXTUAL_PARAM_VALUE") and para_obj.ECUC_TEXTUAL_PARAM_VALUE:
            for i in range(len(para_obj.ECUC_TEXTUAL_PARAM_VALUE)):
                cls.get_para_element(para_obj.ECUC_TEXTUAL_PARAM_VALUE[i], all_element_items_list, filter_text)

    @classmethod
    def traversal_ref_values_global_filter(cls, ref_obj, all_element_items_list, filter_text=None):
        if hasattr(ref_obj, "ECUC_INSTANCE_REFERENCE_VALUE") and ref_obj.ECUC_INSTANCE_REFERENCE_VALUE:
            for i in range(len(ref_obj.ECUC_INSTANCE_REFERENCE_VALUE)):
                cls.get_ref_element(
                    ref_obj.ECUC_INSTANCE_REFERENCE_VALUE[i], all_element_items_list, "iref", filter_text
                )

        if hasattr(ref_obj, "ECUC_REFERENCE_VALUE") and ref_obj.ECUC_REFERENCE_VALUE:
            for i in range(len(ref_obj.ECUC_REFERENCE_VALUE)):
                cls.get_ref_element(ref_obj.ECUC_REFERENCE_VALUE[i], all_element_items_list, "ref", filter_text)

    @classmethod
    def traversal_sub_container_global_filter(cls, containers, all_element_items_list, filter_text):

        sub_containers = containers.SUB_CONTAINERS
        if sub_containers:
            for i in range(len(sub_containers.ECUC_CONTAINER_VALUE)):
                sub_container = sub_containers.ECUC_CONTAINER_VALUE[i]
                if hasattr(sub_container, "SHORT_NAME") and sub_container.SHORT_NAME:
                    cls.get_container_element(sub_container, all_element_items_list, filter_text)
                if hasattr(sub_container, "PARAMETER_VALUES") and sub_container.PARAMETER_VALUES:
                    cls.traversal_para_values_global_filter(
                        sub_container.PARAMETER_VALUES, all_element_items_list, filter_text
                    )
                if hasattr(sub_container, "REFERENCE_VALUES") and sub_container.REFERENCE_VALUES:
                    cls.traversal_ref_values_global_filter(
                        sub_container.REFERENCE_VALUES, all_element_items_list, filter_text
                    )
                cls.traversal_sub_container_global_filter(sub_container, all_element_items_list, filter_text)

    @classmethod
    def get_all_element_items_by_filter_value(cls, ecuc_autosar_dict, filter_value):
        all_element_items_by_filter_value_dict = {}
        for module_name, module_object in ecuc_autosar_dict.items():
            reference_object = module_object.find("/ActiveEcuC/" + module_name)
            containers = reference_object.CONTAINERS.parent_object_.CONTAINERS.ECUC_CONTAINER_VALUE
            for i in range(len(containers)):
                container = containers[i]
                if hasattr(container, "SHORT_NAME") and container.SHORT_NAME:
                    if filter_value in container.SHORT_NAME.valueOf_.lower():
                        logger.debug("short Name匹配")
                if hasattr(container, "PARAMETER_VALUES") and container.PARAMETER_VALUES:
                    cls.traversal_para_values_global_filter(
                        container.PARAMETER_VALUES, filter_value, all_element_items_by_filter_value_dict
                    )
                if hasattr(container, "REFERENCE_VALUES") and container.REFERENCE_VALUES:
                    cls.traversal_ref_values_global_filter(
                        container.REFERENCE_VALUES, filter_value, all_element_items_by_filter_value_dict
                    )
                cls.traversal_sub_container_global_filter(
                    container, filter_value, all_element_items_by_filter_value_dict
                )

        return all_element_items_by_filter_value_dict

    @classmethod
    def get_all_element_items(cls, ecuc_autosar_dict, filter_text):
        all_element_items_list = []
        for module_name, module_object in ecuc_autosar_dict.items():
            reference_object = module_object.find("/ActiveEcuC/" + module_name)
            if hasattr(reference_object, "CONTAINERS"):
                containers = reference_object.CONTAINERS.parent_object_.CONTAINERS.ECUC_CONTAINER_VALUE
                for i in range(len(containers)):
                    container = containers[i]
                    if hasattr(container, "SHORT_NAME") and container.SHORT_NAME:
                        cls.get_container_element(container, all_element_items_list, filter_text)
                    if hasattr(container, "PARAMETER_VALUES") and container.PARAMETER_VALUES:
                        cls.traversal_para_values_global_filter(
                            container.PARAMETER_VALUES, all_element_items_list, filter_text
                        )
                    if hasattr(container, "REFERENCE_VALUES") and container.REFERENCE_VALUES:
                        cls.traversal_ref_values_global_filter(
                            container.REFERENCE_VALUES, all_element_items_list, filter_text
                        )
                    cls.traversal_sub_container_global_filter(container, all_element_items_list, filter_text)

        return all_element_items_list

    @classmethod
    def get_element_items_by_module_name(cls, ecuc_autosar_dict, module_name):
        element_items_list = []
        reference_object = ecuc_autosar_dict[module_name].find("/ActiveEcuC/" + module_name)
        containers = reference_object.CONTAINERS.parent_object_.CONTAINERS.ECUC_CONTAINER_VALUE
        for i in range(len(containers)):
            container = containers[i]
            if hasattr(container, "SHORT_NAME") and container.SHORT_NAME:
                cls.get_container_element(container, element_items_list, None)
            if hasattr(container, "PARAMETER_VALUES") and container.PARAMETER_VALUES:
                cls.traversal_para_values_global_filter(container.PARAMETER_VALUES, element_items_list)
            if hasattr(container, "REFERENCE_VALUES") and container.REFERENCE_VALUES:
                cls.traversal_ref_values_global_filter(container.REFERENCE_VALUES, element_items_list)
            cls.traversal_sub_container_with_short_name(container, element_items_list)

        return element_items_list

    @classmethod
    def traversal_sub_container_with_short_name(cls, containers, all_element_items_list):
        sub_containers = containers.SUB_CONTAINERS
        if sub_containers:
            for i in range(len(sub_containers.ECUC_CONTAINER_VALUE)):
                sub_container = sub_containers.ECUC_CONTAINER_VALUE[i]
                if hasattr(sub_container, "PARAMETER_VALUES") and sub_container.PARAMETER_VALUES:
                    cls.traversal_para_values_global_filter(sub_container.PARAMETER_VALUES, all_element_items_list)
                if hasattr(sub_container, "REFERENCE_VALUES") and sub_container.REFERENCE_VALUES:
                    cls.traversal_ref_values_global_filter(sub_container.REFERENCE_VALUES, all_element_items_list)
                cls.traversal_sub_container_global_filter(sub_container, all_element_items_list, None)

    @classmethod
    def get_container_element(cls, container_obj, all_element_items_list, filter_text=None):

        element_item_dict = {}
        element_item_dict["Element"] = container_obj.get_path()
        element_item_dict["Type"] = "Container"
        element_item_dict["Value"] = ""
        if filter_text is None:
            all_element_items_list.append(element_item_dict)
        elif (filter_text is not None) and filter_text in " ".join(
            str(value).lower() for value in element_item_dict.values() if value is not None
        ):
            all_element_items_list.append(element_item_dict)

    @classmethod
    def get_para_element(cls, para_obj, all_element_items_list, filter_text=None):

        element_item_dict = {}
        element_item_dict["Element"] = para_obj.get_path() + "/" + utils.get_definition_ref(para_obj).split("/")[-1]
        element_item_dict["Type"] = "Parameter"
        element_item_dict["Value"] = utils.get_value(para_obj)
        if filter_text is None:
            all_element_items_list.append(element_item_dict)
        elif (filter_text is not None) and filter_text in " ".join(
            str(value).lower() for value in element_item_dict.values() if value is not None
        ):
            all_element_items_list.append(element_item_dict)

    @classmethod
    def get_ref_element(cls, ref_obj, all_element_items_list, ref_type, filter_text=None):

        element_item_dict = {}
        element_item_dict["Element"] = ref_obj.get_path() + "/" + utils.get_definition_ref(ref_obj).split("/")[-1]
        element_item_dict["Type"] = "Parameter"
        if "ref" == ref_type:
            element_item_dict["Value"] = utils.get_value_ref(ref_obj)
        elif "iref" == ref_type:
            element_item_dict["Value"] = utils.get_value_iref(ref_obj)
        if filter_text is None:
            all_element_items_list.append(element_item_dict)
        elif (filter_text is not None) and filter_text in " ".join(
            str(value).lower() for value in element_item_dict.values() if value is not None
        ):
            all_element_items_list.append(element_item_dict)

    ####################################################################################################################
    # Parse autosar ecuc function
    @classmethod
    def get_all_element_items_components_pports_rports(cls, autosar_asw_class, filter_text):
        all_element_items_list = []
        element_item_dict = {}
        sw_components = []
        for comp_type in cls.SUPPORT_COMPONENT_TYPE:
            sw_components += autosar_asw_class.find_nodes(comp_type)

        for sw_component in sw_components:
            pports = []
            rports = []
            if sw_component.PORTS is not None:
                pports = sw_component.PORTS.P_PORT_PROTOTYPE
                rports = sw_component.PORTS.R_PORT_PROTOTYPE
            element_item_dict = {}
            element_item_dict["Element"] = sw_component.get_path()
            element_item_dict["Type"] = "component"
            element_item_dict["Value"] = ""
            if filter_text in " ".join(str(value).lower() for value in element_item_dict.values() if value is not None):
                all_element_items_list.append(element_item_dict)
            if len(pports):
                for pport in pports:
                    element_item_dict = {}
                    element_item_dict["Element"] = pport.get_path()
                    element_item_dict["Type"] = "pport"
                    element_item_dict["Value"] = ""
                    if filter_text in " ".join(
                        str(value).lower() for value in element_item_dict.values() if value is not None
                    ):
                        all_element_items_list.append(element_item_dict)

            if len(rports):
                for rport in rports:
                    element_item_dict = {}
                    element_item_dict["Element"] = rport.get_path()
                    element_item_dict["Type"] = "rport"
                    element_item_dict["Value"] = ""
                    if filter_text in " ".join(
                        str(value).lower() for value in element_item_dict.values() if value is not None
                    ):
                        all_element_items_list.append(element_item_dict)

        return all_element_items_list

    @classmethod
    def get_all_element_items_common(cls, autosar_asw_class, filter_text, element_tag):
        all_element_items_list = []
        element_item_dict = {}
        elements = autosar_asw_class.find_nodes(element_tag)

        for element in elements:
            element_item_dict = {}
            element_item_dict["Element"] = element.get_path()
            element_item_dict["Type"] = element_tag.lower().replace("-", "_")
            element_item_dict["Value"] = ""
            if filter_text in " ".join(str(value).lower() for value in element_item_dict.values() if value is not None):
                all_element_items_list.append(element_item_dict)
            pass

        return all_element_items_list

    @classmethod
    def get_all_element_items_from_asw(cls, autosar_asw_class, filter_text):
        element_items_list = []
        if autosar_asw_class is None:
            return element_items_list
        SUPPORT_TAG = [
            "DATA-CONSTR",
            "COMPU-METHOD",
            "IMPLEMENTATION-DATA-TYPE",
            "SENDER-RECEIVER-INTERFACE",
            "CLIENT-SERVER-INTERFACE",
            "SWC-INTERNAL-BEHAVIOR",
            "INIT-EVENT",
            "BACKGROUND-EVENT",
            "DATA-RECEIVED-EVENT",
            "OPERATION-INVOKED-EVENT",
            "SWC-MODE-SWITCH-EVENT",
            "MODE-SWITCHED-ACK-EVENT",
            "ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT",
            "TIMING-EVENT",
            "SWC-MODE-SWITCH-EVENT",
            "DATA-SEND-COMPLETED-EVENT",
            "DATA-WRITE-COMPLETED-EVENT",
            "RUNNABLES",
            "RUNNABLE-ENTITY",
            "VARIABLE-ACCESS",
        ]

        # 获取asw中所有的component、pport和rport
        rv = cls.get_all_element_items_components_pports_rports(autosar_asw_class, filter_text)
        for element_tag in SUPPORT_TAG:
            rv += cls.get_all_element_items_common(autosar_asw_class, filter_text, element_tag)
        element_items_list = list({tuple(sorted(d.items())): d for d in rv}.values())
        return element_items_list

    @classmethod
    def get_bswmd_autosar_by_module_name(cls, module_name, module_obj):

        if hasattr(module_obj, "AR_PACKAGES"):
            ar_packages = getattr(module_obj, "AR_PACKAGES")
            bswmd_autosar = cls.traversal_ar_packages(module_name, ar_packages)
            return bswmd_autosar

    @classmethod
    def traversal_ar_packages(cls, module_name, ar_packages):
        if hasattr(ar_packages, "AR_PACKAGE") and getattr(ar_packages, "AR_PACKAGE") is not None:
            ar_package_list = getattr(ar_packages, "AR_PACKAGE")
            for ar_package in ar_package_list:
                if hasattr(ar_package, "ELEMENTS") and getattr(ar_package, "ELEMENTS") is not None:
                    element = getattr(ar_package, "ELEMENTS")
                    if hasattr(element, "ECUC_MODULE_DEF") and getattr(element, "ECUC_MODULE_DEF"):
                        ecuc_module_def_list = getattr(element, "ECUC_MODULE_DEF")
                        for ecuc_module_def in ecuc_module_def_list:
                            if utils.get_short_name(ecuc_module_def) == module_name:
                                return ecuc_module_def
                if hasattr(ar_package, "AR_PACKAGES") and getattr(ar_package, "AR_PACKAGES") is not None:
                    return cls.traversal_ar_packages(module_name, getattr(ar_package, "AR_PACKAGES"))

    @classmethod
    def get_sr_var_init_value(cls, datatype, init_value, ind=""):
        # return value are init_value and is_zero
        category = datatype["native_category"]
        if category == "NUMERICAL":
            basetype = datatype["basetype"]
            if basetype[0] == "b":
                # boolean
                if (
                    init_value.get("value", {}).get("value", "FALSE") == "TRUE"
                    or init_value.get("value", {}).get("value", "FALSE") == "True"
                    or init_value.get("value", {}).get("value", "FALSE") == "1"
                ):
                    return "TRUE", False
                else:
                    return "FALSE", True
            elif basetype[0] == "u":
                # unsigned
                if init_value.get("value", {}).get("value", "0U") in ["0U", "0ULL"]:
                    return init_value.get("value", {}).get("value", "0U"), True
                else:
                    return init_value.get("value", {}).get("value", "0U"), False
            elif basetype[0] == "s":
                # signed
                if init_value.get("value", {}).get("value", "0") == "0":
                    return init_value.get("value", {}).get("value", "0"), True
                else:
                    return init_value.get("value", {}).get("value", "0"), False
            elif basetype[0] == "f":
                # - float
                if init_value.get("value", {}).get("value", "0.0F") in ["0.0", "0.0F"]:
                    return init_value.get("value", {}).get("value", "0.0F"), True
                else:
                    return init_value.get("value", {}).get("value", "0.0F"), False
        elif category in {"STRUCTURE", "ARRAY", "UNION"}:
            if cls.are_all_elements_zero(init_value.get("value", {}).get("value", {})):
                return (
                    "{\n    "
                    + ind
                    + cls.__get_complex_datatype_member(
                        init_value.get("value", {}).get("value", {}), is_union=(category == "UNION")
                    )
                    + ind
                    + "\n}",
                    True,
                )
            else:
                return (
                    "{\n    "
                    + ind
                    + cls.__get_complex_datatype_member(
                        init_value.get("value", {}).get("value", {}), is_union=(category == "UNION")
                    )
                    + ind
                    + "\n}",
                    False,
                )

    @classmethod
    def __get_complex_datatype_member(cls, obj, is_union=False) -> str:
        if isinstance(obj, dict):
            ret = ""
            if is_union:
                ret += "{"

            size = len(obj)
            for i, sub in enumerate(obj.values()):
                if not isinstance(sub, dict):
                    ret += str(sub)
                else:
                    ret += "{" + cls.__get_complex_datatype_member(sub) + "}"
                if i != (size - 1):
                    ret += ","

            if is_union:
                ret += "}"
        elif isinstance(obj, list):
            ret = ""
            if is_union:
                ret += "{"

            size = len(obj)
            for i, sub in enumerate(obj):
                if not isinstance(sub, list):
                    ret += str(sub)
                else:
                    ret += "{" + cls.__get_complex_datatype_member(sub) + "}"
                if i != (size - 1):
                    ret += ","

            if is_union:
                ret += "}"
        else:
            ret = obj
        return ret

    @classmethod
    def are_all_elements_zero(cls, item):
        # 如果是字典，则递归检查每个键对应的值
        if isinstance(item, dict):
            return all(cls.are_all_elements_zero(value) for value in item.values())
        # 如果是列表或元组，则递归检查每个元素
        elif isinstance(item, list) or isinstance(item, tuple):
            return all(cls.are_all_elements_zero(elem) for elem in item)
        # 基本数据类型：直接检查是否为0
        else:
            return str(item).lower() in ["0", "0u", "0ull", "0.0", "0.0f", "false"]
