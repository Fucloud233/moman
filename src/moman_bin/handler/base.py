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
    Interface = "interface"


class MomanCmdOperateType(Enum):
    Default = "default"
    Add = "add"
    Remove = "remove"


class MomanCmdBaseConfig:
    # 值得注意的时, 执行 Create 时脚本路径与项目路径不同
    # 其他脚本当前路径都必须是项目路径
    __path: Path
    __operate_type: MomanCmdOperateType

    def __init__(
        self, path: Path, operate_type: MomanCmdOperateType = MomanCmdOperateType.Default
    ):
        self.__path = path
        self.__operate_type = operate_type

    @property
    def path(self) -> Path:
        """脚本执行当前的路径"""
        return self.__path

    @property
    def operate_type(self) -> MomanCmdOperateType:
        return self.__operate_type


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
