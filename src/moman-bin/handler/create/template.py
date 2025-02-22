GITIGNORE_FILE_TEMPLATE = """\
__pycache__

.moman
"""

ROOT_MODULE_CONFIG_TEMPLATE = """\
type: "root"
name: "{project_name}"

entry: "{entry_name}"
interfaces: []
"""


ENTRY_MODULE_CONFIG_TEMPLATE = """\
type: "entry"
name: "{entry_name}"

# 依赖模块列表
dependencies: []

# 依赖 python 模块列表
python-packages: []
"""
