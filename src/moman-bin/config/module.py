from types import NoneType
from typing import Dict, List, Any
from pathlib import Path

from errors import MomanConfigError
from .base import MomanBaseConfig, MomanModuleType


class MomanModuleDependency:
    __interface: str
    __implement: str
    # None 表示配置文件中没有指定，使用默认处理逻辑
    __path: Path | NoneType

    def __init__(self, interface: str, implement: str, path: Path | None):
        self.__interface = interface
        self.__implement = implement
        self.__path = path

    def update_path(self, path: Path):
        self.__path = path

    @property
    def interface(self) -> str:
        return self.__interface

    @property
    def implement(self) -> str:
        return self.__implement

    @property
    def path(self) -> Path | None:
        return self.__path


# entry 和 implement 的模块配置文件是一致的
class MomanModuleConfig(MomanBaseConfig):
    __interface: str
    __dependencies: List[MomanModuleDependency]
    __packages: List[str]

    def __init__(
        self,
        module_type: MomanModuleType,
        name: str,
        interface: str,
        dependencies: List[MomanModuleDependency],
        packages: List[str],
    ):
        super().__init__(module_type, name)
        self.__interface = interface
        self.__dependencies = dependencies
        self.__packages = packages

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MomanModuleConfig":
        base_config = MomanBaseConfig.from_dict(data)
        if base_config.module_type not in [
            MomanModuleType.Entry, MomanModuleType.Implement
        ]:
            raise MomanConfigError(
                "this is not a module, type: %s, name: %s"
                % (base_config.module_type.value, base_config.name)
            )

        interface: str = data.get("interface", "")

        if MomanModuleType.Entry == base_config.module_type:
            interface = "entry"
        if 0 == len(interface):
            raise BaseException("xxx")

        raw_dependencies: List[str] = data.get("dependencies", [])
        packages: List[str] = data.get("python-package", [])

        dependencies = []
        for dependency in raw_dependencies:
            seqs = dependency.split(":")
            if len(seqs) < 2 or len(seqs) > 3:
                raise BaseException("xxx")

            dep_interface = seqs[0]
            dep_name = seqs[1]
            path = None
            if len(seqs) == 3:
                path = Path(seqs[2])
            dependencies.append(
                MomanModuleDependency(dep_interface, dep_name, path)
            )

        return MomanModuleConfig(
            base_config.module_type, base_config.name, interface,
            dependencies, packages
        )

    @property
    def interface(self) -> str:
        return self.__interface

    @property
    def dependencies(self) -> List[MomanModuleDependency]:
        return self.__dependencies

    @property
    def packages(self) -> List[str]:
        return self.__packages
