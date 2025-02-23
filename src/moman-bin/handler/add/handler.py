from typing import List, override
from enum import Enum
from pathlib import Path
import re

from ..base import MomanCmdHandler, MomanCmdKind, MomanCmdBaseConfig

import constants
import utils
from errors import MomanBinError

from info.config.module import MomanModuleDependency
from info.modular import MomanModularInfo


class MomanAddError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("add", message)


class MomanAddType(Enum):
    # 具体的模块依赖
    Dependency = "dependency"
    # python 依赖
    Package = "package"


class MomanAddBaseConfig(MomanCmdBaseConfig):
    __add_type: MomanAddType
    __implement_name: str

    def __init__(self, path: Path, add_type: MomanAddType, implement_name: str):
        super().__init__(path)

        self.__add_type = add_type
        self.__implement_name = implement_name

    @property
    def add_type(self) -> MomanAddType:
        return self.__add_type

    @property
    def implement_name(self) -> str:
        return self.__implement_name


class MomanAddDependencyConfig(MomanAddBaseConfig):
    # 这里不需要传入 path, 因为所有的信息都会添加到 ModularInfo 之中
    # 后续增加 isExternal 的标识，用于处理项目的模块
    __dep_implements: List[str]

    def __init__(self, path: Path, implement_name: str, dep_implements: List[str]):
        super().__init__(path, MomanAddType.Dependency, implement_name)

        self.__dep_implements = dep_implements

    @property
    def dep_implements(self) -> List[str]:
        return self.__dep_implements


class MomanAddPackageConfig(MomanAddBaseConfig):
    __packages: List[str]

    def __init__(self, path: Path, implement_name: str, packages: List[str]):
        super().__init__(path, MomanAddType.Package, implement_name)

        self.__packages = packages

    @property
    def packages(self) -> List[str]:
        return self.__packages


class MomanAddHandler(MomanCmdHandler):
    def __init__(self):
        super().__init__(MomanCmdKind.Add)

    @override
    def invoke(self, config: MomanCmdBaseConfig):
        config: MomanAddBaseConfig = config
        match config.add_type:
            case MomanAddType.Dependency:
                self.__invoke_add_dependency(config)
            case MomanAddType.Package:
                self.__invoke_add_package(config)

    def __invoke_add_dependency(self, config: MomanAddDependencyConfig):
        path = config.path
        implement_name = config.implement_name
        dep_implements = config.dep_implements

        modular = MomanModularInfo.from_path(path)
        module_config, module_config_folder = modular.modules.get(implement_name, None)
        if module_config is None:
            raise MomanAddError("implement {name} not found".format(name=config.implement_name))

        temp_dep_implements: List[str] = []
        for add_dep in dep_implements:
            dep = module_config.dependencies.get(add_dep, None)
            if dep is None:
                temp_dep_implements.append(add_dep)
        dep_implements = temp_dep_implements

        if len(dep_implements) == 0:
            return

        # 针对内部模块而言

        # 先检查 dep 信息是否正确
        add_deps: List[MomanModuleDependency] = []
        for dep_implement in dep_implements:
            module, module_path = modular.modules.get(dep_implement, (None, None))
            if module is None:
                raise MomanAddError(
                    "implement module {name} not found".format(name=dep_implement)
                )

            # 为模块添加路径
            add_deps.append(MomanModuleDependency(module.interface, module.name, module_path))

        modular.add_module_deps(implement_name, add_deps)
        modular.to_path(path)

        # 这里不能使用 yaml 修改, 会导致最终配置文件丢失格式
        module_config_file = module_config_folder.joinpath(constants.MOMAN_MODULE_CONFIG_NAME)
        module_config_str = utils.read_file(module_config_file)

        deps_key_str = "dependencies:"
        raw_deps_key_strs = re.findall(r"dependencies:\s*\[\]", module_config_str)
        print(raw_deps_key_strs)
        if len(raw_deps_key_strs) == 1:
            module_config_str = module_config_str.replace(
                raw_deps_key_strs[0], deps_key_str, 1
            )

        for add_dep in add_deps:
            module_config_str = module_config_str.replace(
                deps_key_str, deps_key_str + "\n  - " + add_dep.implement, 1
            )

        utils.write_file(module_config_file, module_config_str)

    def __invoke_add_package(self, config: MomanAddPackageConfig):
        pass
