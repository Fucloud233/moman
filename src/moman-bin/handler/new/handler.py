from typing import Tuple, override
from types import NoneType, FunctionType
from enum import Enum
from abc import ABCMeta
from pathlib import Path
import re

from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig

import utils
import constants
from errors import MomanNewError
from info.modular import MomanModularInfo
from info.config.module import MomanModuleImplementConfig
from handler import import_utils

from . import template


class MomanNewType(Enum):
    Interface = "interface"
    Implement = "implement"


class MomanNewBaseConfig(MomanCmdBaseConfig):
    __new_type: MomanNewType
    # interface_name 分为全大小 or 全小写两种类型
    __interface_name: str

    def __init__(self, path: Path, new_type: MomanNewType, interface_name: str):
        super().__init__(path)
        self.__new_type = new_type
        self.__interface_name = interface_name

    @property
    def new_type(self) -> MomanNewType:
        return self.__new_type

    @property
    def interface_name(self) -> str:
        return self.__interface_name


class MomanNewInterfaceConfig(MomanNewBaseConfig):
    def __init__(self, path: Path, interface_name: str):
        super().__init__(path, MomanNewType.Interface, interface_name)


class MomanNewImplementConfig(MomanNewBaseConfig):
    __implement_name: str
    __implement_path: str | NoneType

    def __init__(
        self,
        path: Path,
        interface_name: str,
        implement_name: str,
        implement_path: Path | NoneType = None,
    ):
        super().__init__(path, MomanNewType.Implement, interface_name)

        self.__implement_name = implement_name
        self.__implement_path = implement_path

    @property
    def implement_name(self) -> str:
        return self.__implement_name

    @property
    def implement_path(self) -> Path | NoneType:
        return self.__implement_path


class MomanNewHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.New)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        config: MomanNewBaseConfig = config

        match config.new_type:
            case MomanNewType.Interface:
                self.__invoke_interface(config)
            case MomanNewType.Implement:
                self.__invoke_implement(config)

    def __invoke_interface(self, config: MomanNewInterfaceConfig):
        path = config.path
        raw_interface_name = config.interface_name
        interface_name = raw_interface_name.lower()

        interface_code_file, exists = self.__check_interface_exists(path, interface_name)
        if exists:
            raise MomanNewError("interface {name} exists".format(name=interface_name))

        # interface 的类名支持大驼峰和全大写两种显示格式
        # 目前区分方法时根据用户传入的是全大写字符还是其他形式决定的
        interface_class_name = self.__translate_to_class_name(raw_interface_name)

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

    def __invoke_implement(self, config: MomanNewImplementConfig):
        path = config.path
        interface_name = config.interface_name.lower()
        raw_implement_name = config.implement_name
        implement_name = raw_implement_name.lower()

        interface_code_file, exists = self.__check_interface_exists(path, interface_name)
        if not exists:
            raise MomanNewError("interface {name} not found".format(name=interface_name))

        implement_code_file, exists = self.__check_implement_exists(path, interface_name, implement_name)
        if exists:
            raise MomanNewError("implement {name} exists".format(name=implement_name))

        interface_class: ABCMeta = import_utils.import_interface(
            interface_code_file, interface_name
        )

        interface_class_name = interface_class.__name__

        # 使用模板文件生成出对应代码文件
        implement_class_name = self.__translate_to_class_name(raw_implement_name)

        # 为了完美拷贝函数签名，这里只能使用正则匹配进行拷贝
        interface_code = utils.read_file(interface_code_file)
        func_signatures = re.findall(
            r"\s*@abstractmethod\n\s*(def .*:)\n",
            interface_code,
        )

        func_list: str = ""
        for func_signature in func_signatures:
            func_list += template.MOMAN_NEW_FUNC_TEMPLATE.format(signature=func_signature)

        implement_code = template.MOMAN_NEW_IMPLEMENT_TEMPLATE.format(
            interface_name=interface_name,
            interface_class_name=interface_class_name,
            implement_class_name=implement_class_name,
            func_list=func_list,
        )

        implement_code_folder = path.joinpath(interface_name, implement_name)
        implement_code_folder.mkdir(parents=True, exist_ok=True)

        implement_code_file = implement_code_folder.joinpath(
            constants.MOMAN_MODULE_INIT_NAME
        )
        utils.write_file(implement_code_file, implement_code)

        # 创建 module.yaml 文件
        module_config_data = template.MOMAN_NEW_IMPLEMENT_MODULE_TEMPLATE.format(
            implement_name=implement_name,
            interface_name=interface_name
        )

        module_config_file = implement_code_folder.joinpath(constants.MOMAN_MODULE_CONFIG_NAME)
        utils.write_file(module_config_file, module_config_data)

        # 更新 modular 文件
        implement_config = MomanModuleImplementConfig(implement_name, interface_name)
        modular = MomanModularInfo.from_path(path)
        modular.add_implement(implement_config, implement_code_folder)
        modular.to_path(path)

    def __check_interface_exists(self, path: Path, interface_name: str) -> Tuple[Path, bool]:
        """验证接口是否存在 (直接使用文件判断更准确)

        Args:
            path (Path): 项目路径
            interface_name (str): 接口名称

        Returns:
            Tuple[Path, bool] 接口文件位置, 是否存在
        """
        interface_code_file = path.joinpath(
            constants.MOMAN_INTERFACE_FOLDER,
            interface_name + constants.MOMAN_MODULE_PY_PREFIX,
        )

        return interface_code_file, interface_code_file.exists()

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
            interface_name, implement_name, constants.MOMAN_MODULE_INIT_NAME
        )

        return implement_code_file, implement_code_file.exists()

    def __translate_to_class_name(self, raw: str) -> str:
        class_name = raw
        if not raw.isupper():
            class_name = raw[0].upper() + raw[1:].lower()

        return class_name
