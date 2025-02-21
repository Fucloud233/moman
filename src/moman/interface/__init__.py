from abc import ABCMeta, abstractmethod
from typing import TypeVar
from types import NoneType


class MomanModuleInterface(metaclass=ABCMeta):
    __interface_name: str
    __implement_name: str

    def __init__(self, interface_name: str, implement_name: str):
        self.__interface_name = interface_name
        self.__implement_name = implement_name

    # 模块启动时的钩子函数
    @abstractmethod
    def on_start(self):
        pass

    # 模块停止时的钩子函数
    @abstractmethod
    def on_stop(self):
        pass

    # 用于获取依赖模块
    def get_module(self, interface: type["InterfaceT"],
                   implement: str | NoneType = None) -> "InterfaceT":
        from ..manager import MomanModuleManager

        # 获取模块时需要带上自身的信息用于校验
        return MomanModuleManager.instance().get_module(
            # getInterfaceName 静态函数，获取接口的 interfaceName
            self.__interface_name, self.__implement_name, interface.get_interface_name(), implement
        )

    @property
    def interface_name(self) -> str:
        return self.__interface_name

    @property
    def implement_name(self) -> str:
        return self.__implement_name


ENTRY_INTERFACE_NAME = "entry"


class MomanEntryInterface(MomanModuleInterface):
    def __init__(self, implement_name: str):
        super().__init__(ENTRY_INTERFACE_NAME, implement_name)

    @staticmethod
    def get_interface_name() -> str:
        return ENTRY_INTERFACE_NAME


InterfaceT = TypeVar("InterfaceT", bound=MomanModuleInterface)
