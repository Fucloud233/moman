from typing import Dict, Any
from enum import Enum

import errors


class MomanModuleType(Enum):
    Invalid = "invalid"
    Root = "root"
    Entry = "entry"
    Implement = "implement"


class MomanBaseConfig:
    __module_type: MomanModuleType
    __name: str

    def __init__(self, module_type: MomanModuleType, name: str):
        self.__module_type = module_type
        self.__name = name

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MomanBaseConfig":
        raw_module_type: str = data.get("type", "")
        name: str = data.get("name", "")
        if len(raw_module_type) == 0 or len(name) == 0:
            raise errors.MomanConfigError(
                "module type or name is empty, type: %s, name: %s"
                % (raw_module_type, name)
            )

        module_type = MomanModuleType._value2member_map_.get(
            raw_module_type, MomanModuleType.Invalid
        )

        if MomanModuleType.Invalid == module_type:
            raise errors.MomanConfigError(
                "module type is invalid, type: %s" % raw_module_type
            )

        return MomanBaseConfig(module_type, name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.__module_type.value,
            "name": self.__name,
        }

    @property
    def module_type(self) -> MomanModuleType:
        return self.__module_type

    @property
    def name(self) -> str:
        return self.__name
