from typing import Any
from types import NoneType
from abc import ABCMeta, abstractmethod
from pathlib import Path

from moman.interface import MomanModuleInterface


class MomanModuleManager(metaclass=ABCMeta):
    # 提供模型实现的能力
    @abstractmethod
    def get_module(
        self,
        p_interface_name: str,
        p_implement: str,
        c_interface: str,
        c_implement: str | NoneType = None,
    ) -> MomanModuleInterface:
        pass

    @abstractmethod
    def get_config(
        self,
        implement: str,
        key: str,
        default: Any | NoneType
    ) -> Any:
        pass

    @abstractmethod
    def get_entry_module(
        self, entry_name: str, entry_path: Path
    ) -> MomanModuleInterface:
        pass

    @staticmethod
    def instance() -> "MomanModuleManager":
        from .wrapper import moman_manager_wrapper
        return moman_manager_wrapper
