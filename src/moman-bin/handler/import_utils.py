import importlib.util
from enum import Enum
from pathlib import Path
from typing import Any
from types import NoneType


class MomanClassKind(Enum):
    Interface = "Interface"
    Implement = "Implement"


def import_interface(path: Path, interface_name: str) -> Any | NoneType:
    return __inner_import_class(path, interface_name, MomanClassKind.Interface)


def import_implement(path: Path, implement_name: str) -> Any | NoneType:
    return __inner_import_class(path, implement_name, MomanClassKind.Implement)


def __inner_import_class(path: Path, name: str, kind: MomanClassKind) -> Any | NoneType:
    interface_spec = importlib.util.spec_from_file_location(name, path)
    interface_module = importlib.util.module_from_spec(interface_spec)
    interface_spec.loader.exec_module(interface_module)

    interface_cname = name[0].upper() + name[1:] + kind.value
    interface_full_cname = name.upper() + kind.value

    try:
        return getattr(interface_module, interface_cname)
    except AttributeError:
        pass

    try:
        return getattr(interface_module, interface_full_cname)
    except AttributeError:
        pass

    return None
