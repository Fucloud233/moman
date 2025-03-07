from typing import Dict, override
import sys
import os
from pathlib import Path

from moman.manager.wrapper import register_wrapper_manager, get_wrapper_manager

from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig

import constants
from utils import read_yaml
from info.modular import MomanModularInfo
from info.config.module import MomanModuleConfig

from .manger import MomanModuleManagerWrapper


class MomanBuildHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Build)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        path = config.path

        modular_file = path.joinpath(constants.MOMAN_MODULAR_FILE)

        # 初始化 venv 环境
        self.__init_venv(path)

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

    def __init_venv(self, path: Path):
        venv_config_folder = path.joinpath(constants.MOMAN_CACHE_FOLDER + "/venv")
        if not venv_config_folder.exists():
            os.system("python3 -m venv " + str(venv_config_folder))

        activate_venv_script_file = venv_config_folder.joinpath("bin/activate")
        print(activate_venv_script_file)
        os.system("source " + str(activate_venv_script_file))

        modular = MomanModularInfo.from_path(path)
        for package in modular.packages:
            os.system("pip install" + package)

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
