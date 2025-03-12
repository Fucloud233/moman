from typing import Dict, Tuple, override
import sys
import os
from pathlib import Path

from moman.manager.wrapper import register_wrapper_manager, get_wrapper_manager

from moman_bin import constants, utils
from moman_bin.info.modular import MomanModularInfo
from moman_bin.info.config.module import MomanModuleConfig

from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig
from .manger import MomanModuleManagerWrapper


class MomanBuildHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Build)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        path = config.path

        modular_info = MomanModularInfo.from_path(path)

        # 安装 python 库
        self.__install_packages(path, modular_info)

        modules = modular_info.modules
        config_map = utils.read_yaml(path.joinpath(constants.MOMAN_CONFIG_NAME))

        wrapper_manager = MomanModuleManagerWrapper(modules, config_map)
        register_wrapper_manager(wrapper_manager)

        # 加载所有的 interfaces
        sys.path.append(str(path))

        # 启动 modules
        MomanBuildHandler.__start_recursive(modules, modular_info.entry_name)
        entry_module = get_wrapper_manager().get_entry_module(
            modular_info.entry_name, modular_info.entry_path
        )
        entry_module.on_start()

        # 停止 modules
        MomanBuildHandler.__stop_recursive(modules, modular_info.entry_name)
        entry_module = get_wrapper_manager().get_entry_module(
            modular_info.entry_name, modular_info.entry_path
        )
        entry_module.on_stop()

    def __install_packages(self, path: Path, modular: MomanModularInfo):
        requirements_files = path.joinpath(constants.MOMAN_CACHE_FOLDER, "requirements.txt")

        if not requirements_files.exists():
            utils.write_file(requirements_files, "\n".join(modular.packages))
            os.system("pip install -r " + str(requirements_files))
        else:
            packages_set = set(utils.read_file(requirements_files).splitlines())
            for package in modular.packages:
                if package in packages_set:
                    packages_set.remove(package)
            if len(packages_set) != 0:
                packages = " ".join(packages_set)
                os.system("pip install " + packages)
                utils.write_file(requirements_files, "\n".join(modular.packages))

    @staticmethod
    def __start_recursive(
        modules: Dict[str, Tuple[MomanModuleConfig, Path]], cur_name: str
    ):
        module, _ = modules[cur_name]
        deps = module.dependencies
        for dep in deps.values():
            MomanBuildHandler.__start_recursive(modules, dep.implement)

            dep_module_config, _ = modules[dep.implement]
            module = get_wrapper_manager().get_module(
                cur_name, dep_module_config.interface, dep.implement
            )
            module.on_start()

    @staticmethod
    def __stop_recursive(
        modules: Dict[str, Tuple[MomanModuleConfig, Path]],
        cur_name: str,
    ):
        module, _ = modules[cur_name]
        deps = module.dependencies
        for dep in deps.values():
            MomanBuildHandler.__stop_recursive(modules, dep.implement)

            dep_module_config, _ = modules[dep.implement]
            module = get_wrapper_manager().get_module(
                cur_name, dep_module_config.interface, dep.implement
            )
            module.on_stop()
