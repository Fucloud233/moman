from typing import Tuple, override
from abc import ABCMeta
from pathlib import Path
import re

from moman_bin import utils, constants, template
from moman_bin.info.modular import MomanModularInfo
from moman_bin.info.config.module import MomanModuleImplementConfig
from moman_bin.errors import MomanImplementError

from .. import import_utils
from ..base import (
    MomanCmdHandler,
    MomanCmdKind,
    MomanCmdBaseConfig,
    MomanCmdOperateType,
)


class MomanImplementConfig(MomanCmdBaseConfig):
    __interface_name: str
    __implement_name: str

    def __init__(
        self, path: Path, interface_name: str, implement_name: str, operate_type: MomanCmdOperateType
    ):
        super().__init__(path, operate_type)
        self.__interface_name = interface_name
        self.__implement_name = implement_name

    @property
    def interface_name(self) -> str:
        return self.__interface_name

    @property
    def implement_name(self) -> str:
        return self.__implement_name


class MomanImplementHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Interface)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        match config.operate_type:
            case MomanCmdOperateType.Add:
                self.__invoke_add(config)
            case MomanCmdOperateType.Remove:
                pass

    def __invoke_add(self, config: MomanImplementConfig):
        path = config.path
        interface_name = config.interface_name.lower()
        raw_implement_name = config.implement_name
        implement_name = raw_implement_name.lower()

        interface_code_file = path.joinpath(constants.MOMAN_MODULES_FOLDER, interface_name, "interface.py")

        implement_code_file, exists = self.__check_implement_exists(
            path, interface_name, implement_name
        )
        if exists:
            raise MomanImplementError("implement {name} exists".format(name=implement_name))

        interface_class: ABCMeta = import_utils.import_interface(
            interface_code_file, interface_name
        )

        interface_class_name = interface_class.__name__

        # 使用模板文件生成出对应代码文件
        implement_class_name = import_utils.translate_to_class_name(
            raw_implement_name
        )

        # 为了完美拷贝函数签名，这里只能使用正则匹配进行拷贝
        interface_code = utils.read_file(interface_code_file)
        func_signatures = re.findall(
            r"\s*@abstractmethod\n\s*(def .*:)\n",
            interface_code,
        )

        func_list: str = ""
        for func_signature in func_signatures:
            func_list += template.MOMAN_NEW_FUNC_TEMPLATE.format(
                signature=func_signature
            )

        implement_code = template.MOMAN_NEW_IMPLEMENT_TEMPLATE.format(
            implement_name=implement_name,
            upper_implement_name=implement_name.upper(),
            interface_name=interface_name,
            interface_class_name=interface_class_name,
            implement_class_name=implement_class_name,
            func_list=func_list,
        )

        implement_code_folder = path.joinpath(constants.MOMAN_MODULES_FOLDER, interface_name, implement_name)
        implement_code_folder.mkdir(parents=True, exist_ok=True)

        implement_code_file = implement_code_folder.joinpath(
            constants.MOMAN_MODULE_INIT_NAME
        )
        utils.write_file(implement_code_file, implement_code)

        # 创建 module.yaml 文件
        module_config_data = template.MOMAN_NEW_IMPLEMENT_MODULE_TEMPLATE.format(
            implement_name=implement_name, interface_name=interface_name
        )

        module_config_file = implement_code_folder.joinpath(
            constants.MOMAN_MODULE_CONFIG_NAME
        )
        utils.write_file(module_config_file, module_config_data)

        # 更新 modular 文件
        implement_config = MomanModuleImplementConfig(implement_name, interface_name)
        modular = MomanModularInfo.from_path(path)
        modular.add_implement(implement_config, implement_code_folder)
        modular.to_path(path)

    def __check_implement_exists(self, path: Path, interface_name: str, implement_name: str) -> Tuple[Path, bool]:
        """验证模块实现是否存在 (直接使用文件判断更准确)

        Args:
            path (Path): 项目路径
            interface_name (str): 接口名称
            implement_name (str): 实现名称

        Returns:
            Tuple[Path, bool]: 实现文件位置, 是否存在
        """
        implement_code_file = path.joinpath(
            constants.MOMAN_MODULES_FOLDER, interface_name, implement_name, constants.MOMAN_MODULE_INIT_NAME
        )

        return implement_code_file, implement_code_file.exists()
