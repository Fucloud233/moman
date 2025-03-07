from typing import List, Dict, Any

import errors
from .base import MomanModuleType, MomanBaseConfig


class MomanRootConfig(MomanBaseConfig):
    __entry_name: str
    __interfaces: List[str]

    def __init__(self, name: str, entry_name: str, interfaces: List[str]):
        super().__init__(MomanModuleType.Root, name)

        self.__entry_name = entry_name
        self.__interfaces = interfaces

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MomanRootConfig":
        base_config = MomanBaseConfig.from_dict(data)
        if MomanModuleType.Root != base_config.module_type:
            raise errors.MomanConfigError(
                "current module is not root, type: %s"
                % base_config.module_type
            )

        entry_name: str = data.get("entry", "")
        interfaces: List[str] = data.get("interfaces", [])
        if len(entry_name) == 0:
            raise BaseException("xx")

        return MomanRootConfig(base_config.name, entry_name, interfaces)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["entry"] = self.__entry_name
        result["interfaces"] = self.__interfaces

        return result

    @property
    def entry_name(self) -> str:
        return self.__entry_name

    @property
    def interfaces(self) -> List[str]:
        return self.__interfaces
