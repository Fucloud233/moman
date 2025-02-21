from typing import Dict

from .base import MomanCmdKind, MomanCmdBaseConfig, MomanCmdHandler

from .init.handler import MomanInitHandler
from .modular import MomanModularHandler
from .build.handler import MomanBuildHandler

MOMAN_CMD_HANDLER_MAP: Dict[MomanCmdKind, MomanCmdHandler] = {
    MomanCmdKind.Init: MomanInitHandler(),
    MomanCmdKind.Modular: MomanModularHandler(),
    MomanCmdKind.Build: MomanBuildHandler(),
}


class MomanCmdExecutor:
    @staticmethod
    def invoke(cmd_kind: MomanCmdKind, config: MomanCmdBaseConfig):
        handler = MOMAN_CMD_HANDLER_MAP.get(cmd_kind, None)

        if handler is None:
            return

        handler.invoke(config)
