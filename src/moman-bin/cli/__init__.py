from typing import Any
from argparse import ArgumentParser
from pathlib import Path
import os


class MomanCliExecutor:
    __parser: ArgumentParser

    def __init__(self):
        parser = ArgumentParser()

        sub_parsers = parser.add_subparsers()

        parser_create = sub_parsers.add_parser("create", description="create your fist project.")
        parser_create.add_argument("-p", "--path", help="the path of project")
        parser_create.add_argument("-n", "--name", required=True, help="the name of project")
        parser_create.add_argument("-e", "--entry", default="entry", help="the name of first entry module")
        parser_create.add_argument("-g", "--git", action="store_true", help="use git or not, default not")
        parser_create.set_defaults(func=self.__execute_create)

        parser_new = sub_parsers.add_parser("new", description="new module interface or implement")
        parser_new.add_argument("-i", "--interface", required=True, help="the name of interface")
        parser_new.add_argument("-n", "--name", help="the name of implement")
        parser_new.set_defaults(func=self.__execute_new)

        self.__parser = parser

    def exec(self):
        args = self.__parser.parse_args()
        args.func(args)

    def __execute_create(self, args: Any):
        from handler.create.handler import MomanCreateHandler, MomanCreateConfig

        project_path = args.path
        if project_path is not None:
            project_path = Path(project_path)

        config = MomanCreateConfig(
            Path(os.curdir), args.name, project_path, args.entry, args.git
        )
        MomanCreateHandler().invoke(config)

    def __execute_new(self, args: Any):
        from handler.new.handler import MomanNewHandler, MomanNewConfig

        config = MomanNewConfig(Path(os.curdir), args.interface, args.name)
        MomanNewHandler().invoke(config)
