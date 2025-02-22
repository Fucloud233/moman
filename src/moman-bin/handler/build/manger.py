from pathlib import Path
from typing import Dict, Any, override
from types import NoneType

from moman.manager import MomanModuleManager
from moman.interface import MomanModuleInterface

from info.config.module import MomanModuleConfig, MomanModuleDependency
from errors import MomanBuildError
from handler.import_utils import import_implement


class MomanModuleContext:
    __dep_module_object: Dict[str, Any] = {}

    def __init__(self):
        pass

    def save_implement(self, implement_name: str, implement: Any):
        self.__dep_module_object[implement_name] = implement
        pass

    def get_implement(self, implement_name: str) -> Any | NoneType:
        return self.__dep_module_object.get(implement_name, None)


class MomanModuleManagerWrapper(MomanModuleManager):
    # 当前项目的模块依赖配置
    __module_config_map: Dict[str, MomanModuleConfig] = {}

    # 当对象被创建之后，用于缓存在起来，不会重复创建
    __module_contexts: Dict[str, MomanModuleContext] = {}

    def __init__(self, module_config_map: Dict[str, MomanModuleConfig]):
        self.__module_config_map = module_config_map

    @override
    def get_module(
        self,
        p_interface_name: str,
        p_implement: str,
        c_interface: str,
        c_implement: str | NoneType = None,
    ) -> MomanModuleInterface:
        # 1. 校验父模块是否合法
        module_config = self.__module_config_map.get(p_interface_name, None)
        if module_config is None:
            raise MomanBuildError(
                "current module is invalid, %s, %s" % (p_interface_name, p_implement)
            )

        # 2. 自动获取子模块的实现类型
        dep_map: Dict[str, MomanModuleDependency] = {}
        for dep in module_config.dependencies.values():
            if c_interface == dep.interface:
                dep_map[dep.implement] = dep

        dep: MomanModuleDependency | NoneType = None
        if c_implement is None:
            if len(dep_map) == 1:
                dep = list(dep_map.values())[0]
            elif len(dep_map) > 1:
                raise MomanBuildError("the implement is ambiguous")
        else:
            dep = dep_map.get(c_implement, None)

        if dep is None:
            raise MomanBuildError(
                "module not found, interface: %s, implement: %s"
                % (c_interface, c_implement)
            )

        return self.__inner_get_module(p_implement, dep)

    def get_entry_module(
        self, entry_name: str, entry_path: Path
    ) -> MomanModuleInterface:
        module = self.__module_config_map[entry_name]
        dep = MomanModuleDependency(module.interface, module.name, entry_path)
        return self.__inner_get_module(entry_name, dep)

    def __inner_get_module(
        self, p_implement_name: str, dep: MomanModuleDependency
    ) -> MomanModuleInterface:
        # 1. 从缓存中读取
        module_context = self.__module_contexts.get(p_implement_name, None)

        if module_context is not None:
            implement = module_context.get_implement(dep.implement)
            if implement is not None:
                return implement

        # 2. 通过文件读取
        implement_file = dep.path.joinpath("__init__.py")
        implement_t: MomanModuleInterface | NoneType = import_implement(
            implement_file, dep.implement
        )

        if implement_t is None:
            raise MomanBuildError(
                "module %s class not found, path: %s" % (dep.implement, implement_file)
            )
        
        # 构造函数时只需要传入 implement 即可
        implement_c = implement_t(dep.implement)
        self.__module_contexts.setdefault(
            p_implement_name, MomanModuleContext()
        ).save_implement(dep.implement, implement_c)

        return implement_c
