class MomanBinError(BaseException):
    __kind: str
    __message: str

    def __init__(self, kind: str, message: str):
        self.__kind = kind
        self.__message = message

    def __str__(self) -> str:
        return "[%s] %s" % (self.__kind, self.__message)


class MomanCreateError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("create", message)


class MomanModularError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("modular", message)


class MomanBuildError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("build", message)


class MomanConfigError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("config", message)


class MomanInterfaceError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("interface", message)


class MomanImplementError(MomanBinError):
    def __init__(self, message: str):
        super().__init__("implement", message)
