from typing import override
from pathlib import Path

from .base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig

import constants
import errors
from utils import read_yaml, write_yaml
from handler.import_utils import import_interface

from info.config.base import MomanModuleType
from info.config.root import MomanRootConfig
from info.config.module import MomanModuleConfig
from info.modular import MomanModularInfo

# NOTICE: module 的 implement 是全局唯一的


class MomanModularHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Modular)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        self.analyze_project(config.path)

    def analyze_project(self, path: Path):
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
            if import_interface(interface_file, interface) is None:
                raise errors.MomanModularError(
                    "interface class not found, path: %s" % interface_file
                )

        # 读取入口文件的
        entry_config_file = path.joinpath(
            root_config.entry_name, constants.MOMAN_MODULE_CONFIG_NAME
        ).absolute()

        entry_config = MomanModuleConfig.from_dict(
            read_yaml(entry_config_file)
        )
        if MomanModuleType.Entry != entry_config.module_type:
            raise errors.MomanModularError(
                "this is not entry module, name: %s, path: %s" %
                (entry_config.name, entry_config_file)
            )

        # 根据递归文件 BFS 读取所有依赖文件
        module_configs = {entry_config.name: (entry_config, entry_config_file.parent)}
        queue = [entry_config]
        while len(queue) > 0:
            module_config = queue.pop(0)

            deps = module_config.dependencies
            for dep in deps.values():
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

                module_configs[dep_module_config.name] = \
                    (dep_module_config, dep_module_config_file.parent)

        # 保存解析结果
        result = MomanModularInfo(
            root_config.entry_name, entry_config_file.parent,
            root_config.interfaces, module_configs
        )

        result_file = path.joinpath(constants.MOMAN_MODULAR_FILE)
        if not result_file.parent.exists():
            result_file.parent.mkdir()

        write_yaml(result_file, result.to_dict())
