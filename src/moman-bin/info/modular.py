# 项目分析完成之后的持久化数据

from typing import List, Dict, Any
from pathlib import Path

from .config.module import MomanModuleConfig


class MomanModularInfo:
    __entry_name: str
    __entry_path: Path

    __interfaces: List[str]
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
            module_config.name: {
                "name": module_config.name,
                "type": module_config.module_type.value,
                "interface": module_config.interface,
                "path": str(path),
                "dependencies": {
                    dep.implement: {
                        "interface": dep.interface,
                        "name": dep.implement,
                        "path": str(dep.path),
                    }
                    for dep in module_config.dependencies
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
        for key, value in data["modules"].items():
            modules[key] = MomanModuleConfig.from_dict(value)

        return MomanModularInfo(entry_name, entry_path, interfaces, modules)
