"""从 data/ 目录下的 JSON 数据文件读取全站配置。

所有函数均提供 fallback 默认值，数据文件缺失时不会中断构建流程。
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'

_CACHE = {}


def _load(name, default=None):
    """加载指定 JSON 文件，带缓存。"""
    if name in _CACHE:
        return _CACHE[name]
    path = DATA_DIR / name
    if not path.exists():
        _CACHE[name] = default
        return default
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        _CACHE[name] = data
        return data
    except json.JSONDecodeError as e:
        print(f'  警告: 数据文件解析失败 {name}: {e}')
        _CACHE[name] = default
        return default


def clear_cache():
    """清空缓存，用于需要重新加载数据文件时。"""
    _CACHE.clear()


# ── data/config.json ─────────────────────────────────────

def get_site_title(default="Tritium79's Blog"):
    config = _load('config.json', {})
    return config.get('site', {}).get('title', default) if config else default


def get_site_url(default='https://Tritium79.github.io'):
    config = _load('config.json', {})
    return config.get('site', {}).get('url', default) if config else default


def get_html_lang(default='zh-CN'):
    config = _load('config.json', {})
    return config.get('html_lang', default) if config else default


def get_avatar(default='avatar.png'):
    config = _load('config.json', {})
    return config.get('avatar', default) if config else default


def get_css_file(default='style.css'):
    config = _load('config.json', {})
    return config.get('css_file', default) if config else default


def get_footer(default=None):
    if default is None:
        default = '&copy; 2026 <a href="https://Tritium79.github.io">Tritium79</a>. All rights reserved.'
    config = _load('config.json')
    if config and 'footer' in config:
        return config['footer']
    return default


def get_nav(default=None):
    if default is None:
        default = [
            ('index.html', '首页', 'Domus'),
            ('pages/sylvae.html', '随笔', 'Sylvae'),
            ('pages/commentarii.html', '记录', 'Commentarii'),
            ('pages/interpretationes.html', '译文', 'Interpretationes'),
            ('pages/tabularium.html', '存档', 'Tabularium'),
            ('pages/amici.html', '友链', 'Amici'),
            ('pages/deme.html', '关于', 'De Me'),
        ]
    config = _load('config.json')
    if config and 'nav' in config:
        return [(item['href'], item['cn'], item['la']) for item in config['nav']]
    return default


# ── data/settings.json ──────────────────────────────────

def get_settings(key=None, default=None):
    """读取 data/settings.json，可指定 key 取子字段。"""
    data = _load('settings.json', {})
    if key is None:
        return data
    return data.get(key, default) if data else default
