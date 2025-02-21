from pathlib import Path
from typing import Dict
import sys

from moman.manager.wrapper import register_wrapper_manager, get_wrapper_manager

import constants
from utils import read_yaml
from info.modular import MomanModularInfo
from info.config.module import MomanModuleConfig

from .manger import MomanModuleManagerWrapper


class MomanBuildHandler:
    @staticmethod
    def invoke(path: Path):
        modular_file = path.joinpath(constants.MOMAN_MODULAR_FILE)

        modular_info = MomanModularInfo.from_dict(read_yaml(modular_file))
        modules = modular_info.modules

        wrapper_manager = MomanModuleManagerWrapper(modules)
        register_wrapper_manager(wrapper_manager)

        # 加载所有的 interfaces
        sys.path.append(str(path))

        # 启动 modules
        MomanBuildHandler.__start_recursive(
            modules, modular_info.entry_name, modular_info.entry_name
        )
        entry_module = get_wrapper_manager().get_entry_module(
            modular_info.entry_name, modular_info.entry_path
        )
        entry_module.on_start()

        # 停止 modules
        MomanBuildHandler.__stop_recursive(
            modules, modular_info.entry_name, modular_info.entry_name
        )
        entry_module = get_wrapper_manager().get_entry_module(
            modular_info.entry_name, modular_info.entry_path
        )
        entry_module.on_stop()

    @staticmethod
    def __start_recursive(
        modules: Dict[str, MomanModuleConfig], cur_interface: str, cur_name: str
    ):
        deps = modules[cur_name].dependencies
        for dep in deps.values():
            MomanBuildHandler.__start_recursive(modules, dep.interface, dep.implement)
            module = get_wrapper_manager().get_module(
                cur_interface, cur_name, dep.interface, dep.implement
            )
            module.on_start()

    @staticmethod
    def __stop_recursive(
        modules: Dict[str, MomanModuleConfig], cur_interface: str, cur_name: str
    ):
        deps = modules[cur_name].dependencies
        for dep in deps.values():
            MomanBuildHandler.__stop_recursive(modules, dep.implement, dep.implement)
            module = get_wrapper_manager().get_module(
                cur_interface, cur_name, dep.interface, dep.implement
            )
            module.on_stop()
