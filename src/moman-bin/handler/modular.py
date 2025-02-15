import importlib.util
from typing import Dict, Any
from pathlib import Path
import importlib

import constants
import errors
from utils import read_yaml, write_yaml

from config.base import MomanModuleType
from config.root import MomanRootConfig
from config.module import MomanModuleConfig


class MomanModularHandler:
    @staticmethod
    def modular(path: Path):
        MomanModularHandler.analyze_project(path)

    @staticmethod
    def analyze_project(path: Path):
        # 读取根项目的模块配置文件
        root_config_file = path.joinpath(
            constants.MOMAN_MODULE_CONFIG_NAME
        )

        if not root_config_file.exists():
            raise errors.MomanModularError("root module config not found")

        root_config = MomanRootConfig.from_dict(read_yaml(root_config_file))

        # 校验声明的 interface 对象是否存在
        for interface in root_config.interfaces:
            interface_file = path.joinpath(
                "interface", interface + ".py"
            )

            if not interface_file.exists():
                raise errors.MomanModularError(
                    "interface file not found, path: %s" % interface_file
                )

            # 校验模块文件中的对象是否存在
            interface_spec = importlib.util.spec_from_file_location(
                interface, interface_file
            )
            interface_module = importlib.util.module_from_spec(interface_spec)
            interface_spec.loader.exec_module(interface_module)

            interface_cname = \
                interface[0].upper() + interface[1:] + "Interface"
            interface_cname_full_upper = interface.upper() + "Interface"

            interface_file_exists = False
            try:
                getattr(interface_module, interface_cname)
                interface_file_exists = True
            except AttributeError:
                pass

            try:
                getattr(interface_module, interface_cname_full_upper)
                interface_file_exists = True
            except AttributeError:
                pass

            if not interface_file_exists:
                raise errors.MomanModularError(
                    "interface class not found, path: %s" % interface_file
                )

        # 读取入口文件的
        entry_config_file = path.joinpath(
            root_config.entry_name, constants.MOMAN_MODULE_CONFIG_NAME
        )

        entry_config = MomanModuleConfig.from_dict(
            read_yaml(entry_config_file)
        )
        if MomanModuleType.Entry != entry_config.module_type:
            raise errors.MomanModularError(
                "this is not entry module, name: %s, path: %s" %
                (entry_config.name, entry_config_file)
            )

        # 根据递归文件 BFS 读取所有依赖文件
        module_configs = {entry_config_file.parent: entry_config}
        queue = [entry_config]
        while len(queue) > 0:
            module_config = queue.pop(0)

            deps = module_config.dependencies
            for dep in deps:
                # 判断指定的 interface 是否存在
                if dep.interface not in root_config.interfaces:
                    raise errors.MomanModularError(
                        "interface %s from %s(%s) not found in project" %
                        (
                            dep.interface, module_config.name,
                            module_config.interface
                        )
                    )

                # 如果 path 为空，则使用 root/interface/implement 拼接
                if dep.path is None:
                    dep.update_path(
                        path.joinpath(dep.interface, dep.implement)
                    )

                dep_module_config_file = dep.path.joinpath(
                    constants.MOMAN_MODULE_CONFIG_NAME
                )

                dep_module_config = MomanModuleConfig.from_dict(
                    read_yaml(dep_module_config_file)
                )

                module_configs[dep_module_config_file.parent] = \
                    dep_module_config

        # 保存解析结果
        result = MomanModularHandler.__wrap_modular_result(
            root_config, entry_config_file.parent, module_configs
        )

        result_file_path = path.joinpath(".moman")
        if not result_file_path.exists():
            result_file_path.mkdir()

        write_yaml(result_file_path.joinpath("modular.yaml"), result)

    @staticmethod
    def __wrap_modular_result(
            root_config: MomanRootConfig, entry_path: Path,
            module_configs: Dict[Path, MomanModuleConfig]) -> Dict[str, Any]:
        modular_result: Dict[str, Any] = {}

        modular_result["entry"] = {
            "name": root_config.entry_name, "path": str(entry_path)
        }

        modular_result["interfaces"] = root_config.interfaces

        # 这里统一使用 interface:name key 值，方便索引
        modular_result["modules"] = {
            ("%s:%s" % (module_config.interface, module_config.name)): {
                "name": module_config.name,
                "interface": module_config.interface,
                "path": str(path),
                "dependencies": {
                    ("%s:%s" % (dep.interface, dep.implement)): {
                        "interface": dep.interface,
                        "name": dep.implement,
                        "path": str(dep.path),
                    }
                    for dep in module_config.dependencies
                },
                "packages": module_config.packages,
            }
            for path, module_config in module_configs.items()
        }

        package_count: Dict[str, int] = {}
        for module_config in module_configs.values():
            for package in module_config.packages:
                count = package_count.get(package, 0) + 1
                package_count[package] = count
        modular_result["packageCount"] = package_count

        return modular_result
