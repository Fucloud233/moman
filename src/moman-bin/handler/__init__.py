from pathlib import Path

from .modular import MomanModularHandler
from .build import MomanBuildHandler


class MomanCmdHandler:
    @staticmethod
    def modular(path: Path):
        MomanModularHandler.invoke(path)

    @staticmethod
    def build(path: Path):
        MomanBuildHandler.invoke(path)
