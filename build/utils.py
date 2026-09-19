"""工具函数：干支日期、slug 化、用户交互、front matter 解析、路径容错。"""

import re
import unicodedata
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_settings, ROOT_DIR

# 成对包裹引号映射（ASCII + 中文引号），供路径输入去引号使用
_QUOTE_PAIRS = {'"': '"', "'": "'", '\u201c': '\u201d', '\u2018': '\u2019'}
_ZERO_WIDTH_CHARS = '\ufeff\u200b\u200c\u200d'

try:
    from lunar_python import Solar
except ImportError:
    Solar = None


def get_lunar_date(target_date=None):
    now = target_date if target_date else datetime.now()
    months = get_settings('month_abbreviations',
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    month_abbr = months[now.month - 1]

    if Solar is None:
        raise RuntimeError('lunar_python 未安装，请运行: pip install lunar_python')

    solar = Solar.fromDate(now)
    lunar = solar.getLunar()

    year_gz = lunar.getYearInGanZhi()
    month_gz = lunar.getMonthInGanZhi()
    day_gz = lunar.getDayInGanZhi()

    fmt = get_settings('date_format',
        '{day} {month_abbr}. {year} / {year_gz}年 {month_gz}月 {day_gz}日')
    return fmt.format(day=now.day, month_abbr=month_abbr, year=now.year,
                      year_gz=year_gz, month_gz=month_gz, day_gz=day_gz)


def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\u4e00-\u9fff-]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    words = text.split('-')
    def capitalize_word(word):
        return word if word.isupper() else word.capitalize()
    return '-'.join(capitalize_word(word) for word in words if word)


def make_folder_name(title, date_obj=None):
    slug = slugify(title)
    date_str = date_obj.strftime('%Y%m%d') if date_obj else datetime.now().strftime('%Y%m%d')
    return f'{date_str}_{slug}'


def parse_date_to_ymd(date_str):
    months = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
    }
    m = re.search(r'(\d{1,2})\s+(\w{3})\.\s+(\d{4})', date_str)
    if m:
        day, mon, year = int(m.group(1)), months.get(m.group(2), 1), int(m.group(3))
        return f'{year:04d}{mon:02d}{day:02d}'
    return None


# ── 路径输入容错 ─────────────────────────────────────────
# 终端粘贴路径时常见问题：成对包裹引号、全角字符、零宽/不可见字符、
# Unicode 规范化差异等，导致 Path 精确匹配失败。以下函数生成候选变体并逐一探测。

def _strip_quotes(s):
    """去除成对包裹的引号（ASCII 与中文引号）。"""
    if len(s) >= 2 and s[0] in _QUOTE_PAIRS and s[-1] == _QUOTE_PAIRS[s[0]]:
        return s[1:-1]
    return s


def _halfwidth(s):
    """全角字符 → 半角变体（含全角空格 → 普通空格）。"""
    return ''.join(
        chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E
        else (' ' if c == '\u3000' else c)
        for c in s
    )


def _path_variants(raw):
    """生成路径输入的候选字符串（去引号、NFC、全角→半角），保序去重。"""
    s = raw.strip().strip(_ZERO_WIDTH_CHARS)
    base = _strip_quotes(s).strip().strip(_ZERO_WIDTH_CHARS)
    variants = []
    for v in (base,
              unicodedata.normalize('NFC', base),
              _halfwidth(base),
              unicodedata.normalize('NFC', _halfwidth(base))):
        if v and v not in variants:
            variants.append(v)
    return variants


def resolve_md_path(raw):
    """将用户输入的 Markdown 路径解析为可用的 Path。

    依次尝试：项目根目录相对路径、当前工作目录相对路径、绝对路径原样匹配。
    优先返回已存在的文件；全部找不到时返回按 ROOT_DIR 拼接的兜底 Path
    （保持与原 resolve_path 一致的报错路径）。
    """
    if raw is None:
        return None
    raw_s = raw.strip()
    for cand in _path_variants(raw_s):
        p = Path(cand)
        if p.is_absolute():
            if p.exists():
                return p
            continue
        for base in (ROOT_DIR, Path.cwd()):
            probe = base / cand
            if probe.exists():
                return probe
    p0 = Path(raw_s)
    return p0 if p0.is_absolute() else ROOT_DIR / p0


def path_input_hint(raw):
    """检测输入是否带可自动修正的字符，返回提示文案（找不到文件时打印）。"""
    if not raw:
        return ''
    s = raw.strip()
    tips = []
    if len(s) >= 2 and s[0] in _QUOTE_PAIRS and s[-1] == _QUOTE_PAIRS[s[0]]:
        tips.append('路径被成对引号包裹，已自动去除引号重试')
    if any(0xFF01 <= ord(c) <= 0xFF5E or c == '\u3000' for c in s):
        tips.append('路径含全角字符，已自动转半角重试')
    if any(c in _ZERO_WIDTH_CHARS for c in s):
        tips.append('路径含不可见字符（零宽/BOM），已自动剔除重试')
    return '  ' + '；'.join(tips) if tips else ''


def ask(prompt, default=None):
    if default is not None:
        raw = input(f'{prompt} [{default}]: ').strip()
        return raw if raw else default
    return input(f'{prompt}: ').strip()


def confirm(prompt, default='y'):
    default_show = 'y' if default == 'y' else 'n'
    raw = input(f'{prompt} [{default_show}]: ').strip().lower()
    return raw if raw else default


def parse_front_matter(text):
    pattern = r'^---\n(.*?)\n---\n(.*)'
    match = re.match(pattern, text, re.DOTALL)
    if not match:
        return {}, text.strip()
    meta = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            meta[key.strip()] = val.strip()
    return meta, match.group(2).strip()
