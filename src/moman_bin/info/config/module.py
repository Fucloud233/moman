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
    __dependencies: Dict[str, MomanModuleDependency]
    __packages: List[str]

    def __init__(
        self,
        module_type: MomanModuleType,
        name: str,
        interface: str,
        dependencies: Dict[str, MomanModuleDependency] = {},
        packages: List[str] = [],
    ):
        super().__init__(module_type, name)
        self.__interface = interface
        self.__packages = packages
        self.__dependencies = dependencies

    def add_dep(self, dep: MomanModuleDependency):
        self.dependencies[dep.implement] = dep

    def add_package(self, package: str):
        self.packages.append(package)

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

        raw_dependencies: List | Dict = data.get("dependencies", [])
        if isinstance(raw_dependencies, Dict):
            raw_dependencies = raw_dependencies.values()

        def parse_dep_item(dep_data: str | Dict) -> MomanModuleDependency:
            if isinstance(dep_data, str):
                seqs = dep_data.split(":")
                if len(seqs) < 2 or len(seqs) > 3:
                    raise BaseException("xxx")

                dep_interface = seqs[0]
                dep_implement = seqs[1]
                path = None
                if len(seqs) == 3:
                    path = Path(seqs[2])
            else:
                dep_interface = dep_data["interface"]
                dep_implement = dep_data["implement"]
                path = Path(dep_data["path"])

            return MomanModuleDependency(dep_interface, dep_implement, path)

        dependencies = {}
        for raw_dep in raw_dependencies:
            dep = parse_dep_item(raw_dep)
            dependencies[dep.implement] = dep

        packages: List[str] = data.get("python-package", [])

        return MomanModuleConfig(
            base_config.module_type, base_config.name, interface,
            dependencies, packages
        )

    @property
    def interface(self) -> str:
        return self.__interface

    @property
    def dependencies(self) -> Dict[str, MomanModuleDependency]:
        return self.__dependencies

    @property
    def packages(self) -> List[str]:
        return self.__packages


class MomanModuleEntryConfig(MomanModuleConfig):
    def __init__(
        self,
        name: str,
        interface: str,
        dependencies: Dict[str, MomanModuleDependency] = {},
        packages: List[str] = [],
    ):
        super().__init__(
            MomanModuleType.Entry, name, interface, dependencies, packages
        )


class MomanModuleImplementConfig(MomanModuleConfig):
    def __init__(
        self,
        name: str,
        interface: str,
        dependencies: Dict[str, MomanModuleDependency] = {},
        packages: List[str] = [],
    ):
        super().__init__(MomanModuleType.Implement, name, interface, dependencies, packages)
