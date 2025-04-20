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
"""
配置代码生成模块.
根据输入的config.json, 然后生成模块代码.
"""
import os
from . import context
from func_module.health_monitor.logger import logger
from jinja2 import Environment, FileSystemLoader, StrictUndefined

CUR_FILE_PATH = os.path.dirname(__file__)
DEFAULT_TEMPLATE_FILE_DIR = os.path.join(CUR_FILE_PATH, "template")


def generate_project_makefile(sys_config: dict):
    mk_result_dict = {"makefile": {"result": False}}
    logger.debug("Generate makefile dynamic code")
    try:
        template_dir = os.path.join(DEFAULT_TEMPLATE_FILE_DIR)
        output_dir = os.path.realpath(os.path.join(sys_config["gendata_path"]))
        # Build our rendering environment.
        env = Environment(loader=FileSystemLoader(os.path.abspath(template_dir)), undefined=StrictUndefined)
        env.filters.update(context.get_filters())
        env.globals.update(context.get_functions())
        # Create required directories
        os.makedirs(output_dir, exist_ok=True)
        mk_config = {"sys_config": sys_config}
        render_makefile_generate_mk_file(env, output_dir, mk_config)
        mk_result_dict.update({"makefile": {"result": True}})
        logger.info(f"Finish generating {output_dir}makefile_generated.mk file")
    except Exception:
        logger.exception("Error generating Makefile")
        return mk_result_dict

    return mk_result_dict


def render_makefile_generate_mk_file(env, output_dir, mk_config):

    template = env.get_template("makefile_generated.mk.jinja2")
    file_path = os.path.join(output_dir, "makefile_generated.mk")
    if template is not None:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as out_stream:
            out_stream.write(template.render(mk_config))
