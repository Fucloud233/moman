from types import NoneType
from moman.manager import MomanModuleManager

moman_manager_wrapper: MomanModuleManager | NoneType = None


def register_wrapper_manager(manger: MomanModuleManager):
    global moman_manager_wrapper
    moman_manager_wrapper = manger


def get_wrapper_manager() -> MomanModuleManager:
    return moman_manager_wrapper
