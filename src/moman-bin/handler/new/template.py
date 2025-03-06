MOMAN_NEW_INTERFACE_TEMPLATE = """\
from abc import abstractmethod
from moman.interface import MomanModuleInterface

{upper_interface_name}_INTERFACE_NAME = "{interface_name}"


class {interface_class_name}Interface(MomanModuleInterface):
    def __init__(self, implement_name: str):
        super().__init__(LLM_INTERFACE_NAME, implement_name)

    @staticmethod
    def get_interface_name() -> str:
        return {upper_interface_name}_INTERFACE_NAME

    # 在下面定义你需要的抽象方法

    @abstractmethod
    def your_function(self, param1: str, param2: int) -> str:
        pass
"""

MOMAN_NEW_IMPLEMENT_TEMPLATE = """\
from typing import override
from {interface_name}.interface import {interface_class_name}


class {implement_class_name}Implement({interface_class_name}):
    def __init__(self):
        pass

    @override
    def on_start(self):
        pass

    @override
    def on_stop(self):
        pass

    # 在下面实现之前定义的接口

{func_list}
"""

MOMAN_NEW_FUNC_TEMPLATE = """\
    @override
    {signature}
        pass"""

MOMAN_NEW_IMPLEMENT_MODULE_TEMPLATE = """\
type: "implement"
name: "{implement_name}"
interface: "{interface_name}"

# 依赖的模块内容
dependencies: []

# 依赖的 python 模块内容
python-package: []
"""
