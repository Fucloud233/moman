from typing import Tuple, override
from pathlib import Path

from moman_bin import utils, constants
from moman_bin.info.modular import MomanModularInfo
from moman_bin.errors import MomanInterfaceError

from .. import import_utils
from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig, MomanCmdOperateType
from .. import template


class MomanInterfaceConfig(MomanCmdBaseConfig):
    __interface_name: str

    def __init__(
        self,
        path: Path,
        interface_name: str,
        operate_type: MomanCmdOperateType
    ):
        super().__init__(path, operate_type)
        self.__interface_name = interface_name

    @property
    def interface_name(self) -> str:
        return self.__interface_name


class MomanInterfaceHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Interface)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        match config.operate_type:
            case MomanCmdOperateType.Add:
                self.__invoke_add(config)
            case MomanCmdOperateType.Remove:
                pass

    def __invoke_add(self, config: MomanInterfaceConfig):
        path = config.path
        raw_interface_name = config.interface_name
        interface_name = raw_interface_name.lower()

        interface_code_file, exists = self.__check_interface_exists(path, interface_name)
        if exists:
            raise MomanInterfaceError("interface {name} exists".format(name=interface_name))

        interface_code_folder = path.joinpath(interface_name)
        interface_code_folder.mkdir(exist_ok=True)

        # interface 的类名支持大驼峰和全大写两种显示格式
        # 目前区分方法时根据用户传入的是全大写字符还是其他形式决定的
        interface_class_name = import_utils.translate_to_class_name(raw_interface_name)

        interface_code = template.MOMAN_NEW_INTERFACE_TEMPLATE.format(
            interface_name=interface_name,
            upper_interface_name=interface_name.upper(),
            interface_class_name=interface_class_name,
        )

        utils.write_file(interface_code_file, interface_code)

        # 更新 modular 文件
        modular = MomanModularInfo.from_path(path)
        modular.add_interface(interface_name)
        modular.to_path(path)

    def __check_interface_exists(
        self, path: Path, interface_name: str
    ) -> Tuple[Path, bool]:
        """验证接口是否存在 (直接使用文件判断更准确)

        Args:
            path (Path): 项目路径
            interface_name (str): 接口名称

        Returns:
            Tuple[Path, bool] 接口文件位置, 是否存在
        """
        interface_code_file = path.joinpath(
            interface_name,
            constants.MOMAN_INTERFACE_FOLDER + constants.MOMAN_MODULE_PY_PREFIX,
        )

        return interface_code_file, interface_code_file.exists()
