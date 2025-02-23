# 项目分析完成之后的持久化数据

from typing import List, Dict, Any
from pathlib import Path

from .config.module import MomanModuleConfig


class MomanModularInfo:
    __entry_name: str
    __entry_path: Path

    __interfaces: List[str]
    # MomanModuleConfig 本身不存储 path, 因此使用 path 作为 key 值
    __modules: Dict[str, MomanModuleConfig]
    __package_count: Dict[str, int] = {}

    def __init__(self, entry_name: str, entry_path: Path,
                 interfaces: List[str],
                 modules: Dict[str, MomanModuleConfig]):
        self.__entry_name = entry_name
        self.__entry_path = entry_path
        self.__interfaces = interfaces
        self.__modules = modules

        for module_config in modules.values():
            for package in module_config.packages:
                count = self.__package_count.get(package, 0) + 1
                self.__package_count[package] = count

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
            for path, module_config in self.__modules.items()
        }

        result["packageCount"] = self.__package_count

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MomanModularInfo":
        entry_name = data["entry"]["name"]
        entry_path = Path(data["entry"]["path"])

        interfaces = data["interfaces"]

        modules: Dict[str, MomanModuleConfig] = {}
        for value in data["modules"].values():
            modules[Path(value["path"])] = MomanModuleConfig.from_dict(value)

        return MomanModularInfo(entry_name, entry_path, interfaces, modules)

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
    def modules(self) -> Dict[str, MomanModuleConfig]:
        return self.__modules

    @property
    def package_count(self) -> Dict[str, int]:
        return self.__package_count
