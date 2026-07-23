"""全局常量。

ARCHETYPE_PATH：模板文件路径
CATEGORIES / SECTION_MAP / PAGE_MAP：从 data/categories.json 加载
ENTRY_TEMPLATE：从 data/settings.json 加载
"""

from pathlib import Path

from data_loader import get_settings

# 目录路径
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
ARCHETYPE_PATH = ROOT_DIR / 'archetypes' / 'archetype.html'

# 从 data/categories.json 加载分类定义
_CAT_FILE = ROOT_DIR / 'data' / 'categories.json'
if _CAT_FILE.exists():
    import json
    with open(_CAT_FILE, encoding='utf-8') as _f:
        _raw = json.load(_f)
else:
    _raw = {}

CATEGORIES = [(k, v['name']) for k, v in _raw.items()]
SECTION_MAP = {k: v['section_cn'] for k, v in _raw.items()}
PAGE_MAP = {k: ROOT_DIR / v['page'] for k, v in _raw.items()}

# 从 data/settings.json 加载汇总页条目模板
ENTRY_TEMPLATE = get_settings('entry_template',
    '<li>\n                    <a\n                        href="../content/%%CATEGORY%%/%%FOLDER%%/index.html"\n                        >%%TITLE%%</a\n                    >\n                    <p class="article-date">\n                        %%DATE%%\n                    </p>\n                </li>')
