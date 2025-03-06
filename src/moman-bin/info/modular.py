# 项目分析完成之后的持久化数据

from typing import List, Dict, Tuple, Any
from pathlib import Path

import constants
import utils

from .config.module import MomanModuleConfig, MomanModuleDependency


class MomanModularInfo:
    __entry_name: str
    __entry_path: Path

    __interfaces: List[str]
    # MomanModuleConfig 本身不存储 path, 因此使用 path 作为 key 值
    __modules: Dict[str, Tuple[MomanModuleConfig, Path]]
    __package_count: Dict[str, int] = {}

    def __init__(self, entry_name: str, entry_path: Path,
                 interfaces: List[str],
                 modules: Dict[str, Tuple[MomanModuleConfig, Path]]):
        self.__entry_name = entry_name
        self.__entry_path = entry_path
        self.__interfaces = interfaces
        self.__modules = modules

        for module_config, _ in modules.values():
            for package in module_config.packages:
                count = self.__package_count.get(package, 0) + 1
                self.__package_count[package] = count

    def add_interface(self, interface_name: str):
        self.__interfaces.append(interface_name)

    def add_implement(self, implement: MomanModuleConfig, path: Path):
        self.__modules[implement.name] = (implement, path.absolute())

    def add_module_deps(self, implement_name: str, deps: List[MomanModuleDependency]) -> bool:
        """添加模块依赖，不做复杂的校验，需要外界保证正确

        Args:
            implement_name (str): 实现模块名称
            deps (List[MomanModuleDependency]): 模块依赖列表

        Returns:
            bool: 是否成功添加
        """

        module, _ = self.__modules.get(implement_name, None)
        if module is None:
            return False

        for dep in deps:
            module.add_dep(dep)

        return True

    def add_packages(self, implement_name: str, packages: List[str]) -> bool:
        module, _ = self.__modules.get(implement_name, None)
        if module is None:
            return False

        for package in packages:
            module.add_package(package)

            count = self.__package_count.get(package, 0)
            self.__package_count[package] = count + 1

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        result["entry"] = {
            "name": self.__entry_name, "path": str(self.__entry_path)
        }

        result["interfaces"] = self.__interfaces

        # 这里统一使用 interface:name key 值，方便索引
        result["modules"] = {
            # 这两个概念一致, 命名不同 module.name = dependency.implement
            module_config.name: {
                "name": module_config.name,
                "type": module_config.module_type.value,
                "interface": module_config.interface,
                "path": str(path),
                "dependencies": {
                    dep.implement: {
                        "interface": dep.interface,
                        "implement": dep.implement,
                        "path": str(dep.path),
                    }
                    for dep in module_config.dependencies.values()
                },
                "packages": module_config.packages,
            }
            for module_config, path in self.__modules.values()
        }

        result["packageCount"] = self.__package_count

        return result

    def to_path(self, path: Path):
        info_path = path.joinpath(constants.MOMAN_MODULAR_FILE)
        utils.write_yaml(info_path, self.to_dict())

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MomanModularInfo":
        entry_name = data["entry"]["name"]
        entry_path = Path(data["entry"]["path"])

        interfaces = data["interfaces"]

        modules: Dict[str, MomanModuleConfig] = {}
        for key, value in data["modules"].items():
            modules[key] = (MomanModuleConfig.from_dict(value), Path(value["path"]))

        return MomanModularInfo(entry_name, entry_path, interfaces, modules)

    @staticmethod
    def from_path(path: Path) -> "MomanModularInfo":
        info_path = path.joinpath(constants.MOMAN_MODULAR_FILE)
        return MomanModularInfo.from_dict(utils.read_yaml(info_path))

    @property
    def entry_name(self) -> str:
        return self.__entry_name

    @property
    def entry_path(self) -> Path:
        return self.__entry_path

    @property
    def interfaces(self) -> List[str]:
        return self.__interfaces

    @property
    def modules(self) -> Dict[str, Tuple[MomanModuleConfig, Path]]:
        return self.__modules

    @property
    def package_count(self) -> Dict[str, int]:
        return self.__package_count

    @property
    def packages(self) -> List[str]:
        return self.__package_count.values()
