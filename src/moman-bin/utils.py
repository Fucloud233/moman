from typing import Dict, Any
from pathlib import Path

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
