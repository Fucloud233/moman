from pathlib import Path

from .modular import MomanModularHandler


class MomanCmdHandler:
    @staticmethod
    def modular(path: Path):
        MomanModularHandler.modular(path)
