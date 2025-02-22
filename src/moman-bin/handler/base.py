from abc import ABCMeta, abstractmethod
from enum import Enum
from pathlib import Path


class MomanCmdKind(Enum):
    Create = "create"
    Modular = "modular"
    Build = "build"


class MomanCmdBaseConfig:
    __path: Path

    def __init__(self, path: Path):
        self.__path = path

    @property
    def path(self) -> Path:
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
