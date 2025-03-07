from abc import ABCMeta, abstractmethod
from enum import Enum
from pathlib import Path


class MomanCmdKind(Enum):
    Create = "create"
    Modular = "modular"
    New = "new"
    Add = "add"
    Build = "build"
    Delete = "delete"  # TODO
    Remove = "remove"  # TODO


class MomanCmdBaseConfig:
    # 值得注意的时, 执行 Create 时脚本路径与项目路径不同
    # 其他脚本当前路径都必须是项目路径
    __path: Path

    def __init__(self, path: Path):
        self.__path = path

    @property
    def path(self) -> Path:
        """脚本执行当前的路径"""
        return self.__path


class MomanCmdHandler(metaclass=ABCMeta):
    __cmd_kind: MomanCmdKind

    def __init__(self, cmd_kind: MomanCmdKind):
        self.__cmd_kind = cmd_kind

    @abstractmethod
    def invoke(self, config: MomanCmdBaseConfig):
        pass

    @property
    def cmd_kind(self, ) -> MomanCmdKind:
        return self.__cmd_kind
