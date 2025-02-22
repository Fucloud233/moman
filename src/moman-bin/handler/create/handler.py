from typing import override
import os
from pathlib import Path

from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig
from errors import MomanCreateError

import constants
import utils
from . import template
from ..modular import MomanModularHandler


class MomanCreateConfig(MomanCmdBaseConfig):
    __project_name: str
    __entry_name: str
    __use_git: bool

    def __init__(
        self,
        path: Path,
        project_name: str,
        entry_name: str = constants.MOMAN_ENTRY_DEFAULT_NAME,
        use_git: bool = False,
    ):
        super().__init__(path)
        self.__project_name = project_name
        self.__entry_name = entry_name
        self.__use_git = use_git

    @property
    def project_name(self) -> str:
        """项目名称"""
        return self.__project_name

    @property
    def entry_name(self) -> str:
        """入口文件名称"""
        return self.__entry_name

    @property
    def use_git(self) -> bool:
        return self.__use_git


class MomanCreateHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Create)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        config: MomanCreateConfig = config

        path = config.path
        project_name = config.project_name
        entry_name = config.entry_name

        # 处理项目根目录
        try:
            path.mkdir(exist_ok=False)
        except FileExistsError:
            raise MomanCreateError("path %s is not empty" % str(path))

        # 处理根项目
        path.joinpath(constants.MOMAN_CACHE_FOLDER).mkdir(exist_ok=True)

        root_module_path = path.joinpath(constants.MOMAN_MODULE_CONFIG_NAME)
        utils.write_file(
            root_module_path,
            template.ROOT_MODULE_CONFIG_TEMPLATE.format(
                project_name=project_name, entry_name=entry_name
            ),
        )

        path.joinpath(constants.MOMAN_INTERFACE_FOLDER).mkdir(exist_ok=True)

        # 处理 entry 目录文件
        entry_folder = path.joinpath(entry_name)
        entry_folder.mkdir(exist_ok=True)

        entry_module_file = entry_folder.joinpath(constants.MOMAN_MODULE_CONFIG_NAME)
        utils.write_file(
            entry_module_file,
            template.ENTRY_MODULE_CONFIG_TEMPLATE.format(entry_name=entry_name),
        )

        # 处理 git 相关
        gitignore_file = path.joinpath(constants.MOMAN_GIT_IGNORE_FILE)
        utils.write_file(gitignore_file, template.GITIGNORE_FILE_TEMPLATE)

        if config.use_git:
            os.system("git init %s" % str(path))

        # 最后执行 Modular 逻辑
        MomanModularHandler().invoke(config)
