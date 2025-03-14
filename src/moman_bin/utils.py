from typing import Dict, Any
from pathlib import Path
from enum import Enum

from termcolor import colored
import yaml


def yaml_to_dict(data: str) -> Dict[str, Any]:
    return yaml.safe_load(data)


def read_file(file_path: Path) -> str:
    with open(file_path, "r", encoding="UTF-8") as f:
        return f.read(-1)


def read_yaml(file_path: Path) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        result = yaml.safe_load(f)

        return result


def write_file(file_path: Path, data: str):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)


def write_yaml(file_path: Path, data: Dict[str, Any]):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


class MomanLogType(Enum):
    Verbose = "verbose"
    Debug = "debug"
    Info = "info"
    Ok = "ok"
    Warn = "warn"
    Error = "error"


class MomanLogger:
    @staticmethod
    def verbose(msg: str):
        MomanLogger.__inner_log(MomanLogType.Verbose, msg)

    @staticmethod
    def debug(msg: str):
        MomanLogger.__inner_log(MomanLogType.Debug, msg)

    @staticmethod
    def info(msg: str):
        MomanLogger.__inner_log(MomanLogType.Info, msg)

    @staticmethod
    def ok(msg: str):
        MomanLogger.__inner_log(MomanLogType.Ok, msg)

    @staticmethod
    def warn(msg: str):
        MomanLogger.__inner_log(MomanLogType.Warn, msg)

    @staticmethod
    def error(msg: str):
        MomanLogger.__inner_log(MomanLogType.Error, msg)

    @staticmethod
    def __inner_log(log_type: MomanLogType, msg: str):
        color = ""
        match log_type:
            case MomanLogType.Verbose:
                color = "grey"
            case MomanLogType.Info:
                color = "white"
            case MomanLogType.Debug:
                color = "blue"
            case MomanLogType.Warn:
                color = "yellow"
            case MomanLogType.Error:
                color = "red"
            case MomanLogType.Ok:
                color = "green"

        print(colored("[%s] %s" % (log_type.value, msg), color))
