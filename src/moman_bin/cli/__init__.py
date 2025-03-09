from typing import Any
from argparse import ArgumentParser
from pathlib import Path
import os

from moman_bin.errors import MomanBinError
from moman_bin.utils import MomanLogger


class MomanCliExecutor:
    __parser: ArgumentParser

    def __init__(self):
        parser = ArgumentParser()

        sub_parsers = parser.add_subparsers()

        parser_create = sub_parsers.add_parser(
            "create",
            help="create your fist project.",
            description="create your fist project.",
        )
        parser_create.add_argument("-p", "--path", help="the path of project")
        parser_create.add_argument("-n", "--name", required=True, help="the name of project")
        parser_create.add_argument("-e", "--entry", default="entry", help="the name of first entry module")
        parser_create.add_argument("-g", "--git", action="store_true", help="use git or not, default not")
        parser_create.set_defaults(func=self.__execute_create)

        parser_interface = sub_parsers.add_parser(
            "interface",
            help="operate with the interface of module.",
            description="operate with the interface of module.",
        )
        parser_interface.add_argument("-n", "--new", action="store_true")
        parser_interface.add_argument("-d", "--delete", action="store_true")
        parser_interface.add_argument("name")
        parser_interface.set_defaults(func=self.__execute_interface)

        parser_implement = sub_parsers.add_parser(
            "implement",
            help="operate with the implement of module.",
            description="operate with the implement of module.",
        )
        parser_implement.add_argument("-n", "--new", action="store_true")
        parser_implement.add_argument("-d", "--delete", action="store_true")
        parser_implement.add_argument("-i", "--interface")
        parser_implement.add_argument("name")
        parser_implement.set_defaults(func=self.__execute_implement)

        parser_add = sub_parsers.add_parser(
            "add",
            help="add module dependencies or python packages for module.",
            description="add module dependencies or python packages for module."
        )
        parser_add.add_argument("-n", "--name", required=True)
        parser_add.add_argument("-d", "--deps", default="")
        parser_add.add_argument("-p", "--packages", default="")
        parser_add.set_defaults(func=self.__execute_add)

        parser_add = sub_parsers.add_parser(
            "remove",
            help="remove module dependencies or python packages for module.",
            description="remove module dependencies or python packages for module.",
        )

        parser_build = sub_parsers.add_parser(
            "build",
            help="build this project.",
            description="build this project."
        )
        parser_build.set_defaults(func=self.__execute_build)

        self.__parser = parser

    def exec(self):
        try:
            args = self.__parser.parse_args()
            args.func(args)
        except MomanBinError as e:
            MomanLogger.error(str(e))

    def __execute_create(self, args: Any):
        from moman_bin.handler.create.handler import MomanCreateHandler, MomanCreateConfig

        project_path = args.path
        if project_path is not None:
            project_path = Path(project_path)

        config = MomanCreateConfig(
            Path(os.curdir), args.name, project_path, args.entry, args.git
        )
        MomanCreateHandler().invoke(config)

    def __execute_interface(self, args: Any):
        from moman_bin.handler.interface import MomanInterfaceHandler, MomanInterfaceConfig
        from moman_bin.errors import MomanInterfaceError
        from moman_bin.handler.base import MomanCmdOperateType

        print(args)

        name = args.name
        new_flag = args.new
        delete_flag = args.delete

        if new_flag and delete_flag:
            raise MomanInterfaceError("can not add and delete at the same time")

        operate_type = MomanCmdOperateType.Add
        if delete_flag:
            operate_type = MomanCmdOperateType.Remove

        config = MomanInterfaceConfig(Path(os.curdir), name, operate_type)
        MomanInterfaceHandler().invoke(config)

    def __execute_implement(self, args: Any):
        from moman_bin.handler.implement import (
            MomanImplementHandler,
            MomanImplementConfig,
        )
        from moman_bin.errors import MomanInterfaceError
        from moman_bin.handler.base import MomanCmdOperateType

        print(args)

        name = args.name
        interface = args.interface
        new_flag = args.new
        delete_flag = args.delete

        if new_flag and delete_flag:
            raise MomanInterfaceError("can not add and delete at the same time")

        operate_type = MomanCmdOperateType.Add
        if delete_flag:
            operate_type = MomanCmdOperateType.Remove

        config = MomanImplementConfig(Path(os.curdir), interface, name, operate_type)
        MomanImplementHandler().invoke(config)

    def __execute_add(self, args: Any):
        from moman_bin.handler.add.handler import MomanAddHandler, MomanAddConfig

        dependencies = args.deps.split(" ") if len(args.deps) > 0 else []
        packages = args.packages.split(" ") if len(args.packages) > 0 else []

        config = MomanAddConfig(Path(os.curdir), args.name, dependencies, packages)
        MomanAddHandler().invoke(config)

    def __execute_build(self, args: Any):
        from moman_bin.handler.build.handler import MomanBuildHandler, MomanCmdBaseConfig

        MomanBuildHandler().invoke(MomanCmdBaseConfig(Path(os.curdir)))
