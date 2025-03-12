from typing import override, Dict, Any
from pathlib import Path

from .base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig

from moman_bin import constants, utils
from moman_bin.errors import MomanModularError
from moman_bin.info.config.base import MomanModuleType
from moman_bin.info.config.root import MomanRootConfig
from moman_bin.info.config.module import MomanModuleConfig, MomanConfigType
from moman_bin.info.modular import MomanModularInfo

from .import_utils import import_interface

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
            raise MomanModularError("root module config not found")

        root_config = MomanRootConfig.from_dict(utils.read_yaml(root_config_file))

        # 校验声明的 interface 对象是否存在
        for interface in root_config.interfaces:
            interface_file = path.joinpath(
                constants.MOMAN_MODULES_FOLDER, interface,
                constants.MOMAN_INTERFACE_NAME
            )

            if not interface_file.exists():
                raise MomanModularError(
                    "interface file not found, path: %s" % interface_file
                )

            # 校验模块文件中的对象是否存在
            if import_interface(interface_file, interface) is None:
                raise MomanModularError(
                    "interface class not found, path: %s" % interface_file
                )

        # 读取入口文件的
        entry_config_file = path.joinpath(
            root_config.entry_name, constants.MOMAN_MODULE_CONFIG_NAME
        ).absolute()

        entry_config = MomanModuleConfig.from_dict(utils.read_yaml(entry_config_file))
        if MomanModuleType.Entry != entry_config.module_type:
            raise MomanModularError(
                "this is not entry module, name: %s, path: %s" %
                (entry_config.name, entry_config_file)
            )

        module_configs = {entry_config.name: (entry_config, entry_config_file.parent)}

        # 遍历 modules 目录模块文件
        modules_folder = path.joinpath(constants.MOMAN_MODULES_FOLDER)
        for module_folder, _, _ in modules_folder.walk():
            if module_folder.is_file():
                continue

            module_interface_file = module_folder.joinpath(constants.MOMAN_INTERFACE_NAME)
            if not module_interface_file.exists():
                continue

            for module_impl_folder, _, _ in module_folder.walk():
                if module_impl_folder.is_file():
                    continue

                module_config_file = module_impl_folder.joinpath(constants.MOMAN_MODULE_CONFIG_NAME)
                if not module_config_file.exists():
                    continue

                implement_name = module_impl_folder.name
                utils.MomanLogger.debug("scan module, name: %s" % implement_name)
                module_configs[implement_name] = (MomanModuleConfig.from_dict(utils.read_yaml(module_config_file)), module_impl_folder.absolute())

        # 更新 dep 信息
        for module_config, _ in module_configs.values():
            for dep_name, dep in module_config.dependencies.items():
                _, dep_path = module_configs[dep_name]
                dep.update_path(dep_path)

        # 生成配置文件
        config_file = path.joinpath(constants.MOMAN_CONFIG_NAME)
        if config_file.exists():
            origin_config_map: Dict[str, Dict[str, MomanConfigType]] = utils.read_yaml(
                config_file
            )
        else:
            origin_config_map = {}

        for module, _ in module_configs.values():
            origin_config = origin_config_map.get(module.name, {})
            if origin_config is None:
                origin_config[module.name] = {}

            for key, config_t in module.config_map.items():
                config_value = origin_config.get(key, None)    
                if config_value is not None:
                    continue
                default_value: Any
                match config_t:
                    case MomanConfigType.String:
                        default_value = ""
                    case MomanConfigType.Number:
                        default_value = 0
                    case MomanConfigType.List:
                        default_value = []
                origin_config[key] = default_value

            origin_config_map[module.name] = origin_config

        utils.write_yaml(config_file, origin_config_map)

        # 保存解析结果
        result = MomanModularInfo(
            root_config.entry_name, entry_config_file.parent,
            root_config.interfaces, module_configs
        )

        result_file = path.joinpath(constants.MOMAN_MODULAR_FILE)
        if not result_file.parent.exists():
            result_file.parent.mkdir()

        utils.write_yaml(result_file, result.to_dict())
