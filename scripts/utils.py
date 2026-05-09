import re
from datetime import datetime

try:
    from lunar_python import Solar
except ImportError:
    Solar = None


def get_lunar_date(target_date=None):
    """获取指定日期或当前日期的干支格式。

    Args:
        target_date: datetime 对象，若为 None 则使用当前时间

    格式: [日，数字] [月，缩写]. [年，数字] / [干支]年 [干支]月 [干支]日
    例: 8 May. 2026 / 丙午年 癸巳月 壬午日
    """
    now = target_date if target_date else datetime.now()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_abbr = months[now.month - 1]

    if Solar is None:
        raise RuntimeError('lunar_python 未安装，请运行: pip install lunar_python')

    solar = Solar.fromDate(now)
    lunar = solar.getLunar()

    year_gz = lunar.getYearInGanZhi()
    month_gz = lunar.getMonthInGanZhi()
    day_gz = lunar.getDayInGanZhi()

    return f'{now.day} {month_abbr}. {now.year} / {year_gz}年 {month_gz}月 {day_gz}日'


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
