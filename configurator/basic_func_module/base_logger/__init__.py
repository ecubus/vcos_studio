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
import sys
from loguru._logger import Core, Logger

__all__ = ["BaseLogger"]

DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "[<level>{level}</level>] "
    "<cyan>{file}:{line}</cyan> - <level>{message}</level>"
)

# log level, Option: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
DEFAULT_LEVEL = "INFO"


class BaseLogger(Logger):
    r""" "Base Func Module Logger"""

    def __init__(
        self,
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patcher=None,
        extra=None,
    ):
        if patcher is None:
            patcher = []
        if extra is None:
            extra = {}
        super().__init__(Core(), exception, depth, record, lazy, colors, raw, capture, patcher, extra)

    def add_handler(self, sink, level=DEFAULT_LEVEL, format=DEFAULT_FORMAT, colorize=False, enqueue=False, filter=None):
        if sink is None:
            sink = sys.stderr
        kwargs = {
            "sink": sink,
            "level": level,
            "format": format,
            "colorize": colorize,
            "enqueue": enqueue,
            "catch": True,
            "filter": filter,
        }
        try:
            local_kwargs = kwargs.copy()
            local_kwargs.update({"rotation": "200 MB", "compression": "zip", "encoding": "utf-8"})
            handler_id = self.add(**local_kwargs)
        except TypeError:
            handler_id = self.add(**kwargs)
        return handler_id

    def __getattr__(self, name: str):
        if name.startswith("ui_"):
            name = name[3:]
        attr = self.__getattribute__(name)
        if hasattr(self, "ui_object"):
            return lambda msg, *args, **kwargs: attr(msg, *args, **kwargs, ui_log=True)
        else:
            return attr


logger = BaseLogger()
perf_logger = BaseLogger()
