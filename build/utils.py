"""工具函数：干支日期、slug 化、用户交互、front matter 解析。"""

import re
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_settings

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
