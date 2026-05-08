#!/usr/bin/env python3
"""交互式将 Markdown 文章转换为独立 HTML 页面，并自动更新对应分类页。"""

import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("请先安装依赖: pip install markdown")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = ROOT_DIR / 'template' / 'article.html'

CATEGORIES = [
    ('silvae', '随笔 / Silvae'),
    ('commentarii', '记录 / Commentarii'),
    ('versiones', '译文 / Versiones'),
    ('archivum', '存档 / Archivum'),
]

SECTION_MAP = {
    'silvae': '随笔',
    'commentarii': '记录',
    'versiones': '译文',
    'archivum': '存档',
}

PAGE_MAP = {
    'silvae': ROOT_DIR / 'pages' / 'silvae.html',
    'commentarii': ROOT_DIR / 'pages' / 'commentarii.html',
    'versiones': ROOT_DIR / 'pages' / 'versiones.html',
    'archivum': ROOT_DIR / 'pages' / 'archivum.html',
}

ENTRY_TPL = (
    '                <li>\n'
    '                    <a\n'
    '                        href="../content/%%CATEGORY%%/%%FOLDER%%/index.html"\n'
    '                        >%%TITLE%%</a\n'
    '                    >\n'
    '                    <p class="article-date">\n'
    '                        %%DATE%%\n'
    '                    </p>\n'
    '                </li>'
)


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


def render_markdown(text):
    return markdown.markdown(text, extensions=['extra'])


def fill_template(template, title, date, content, section):
    html = template
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ date }}', date)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ section }}', section)
    return html


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\u4e00-\u9fff-]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def ask(prompt, default=None):
    if default is not None:
        raw = input(f'{prompt} [{default}]: ').strip()
        return raw if raw else default
    return input(f'{prompt}: ').strip()


def add_entry_to_page(page_path, title, date, category, folder):
    if not page_path.exists():
        return

    entry = (ENTRY_TPL
             .replace('%%CATEGORY%%', category)
             .replace('%%FOLDER%%', folder)
             .replace('%%TITLE%%', title)
             .replace('%%DATE%%', date))

    content = page_path.read_text(encoding='utf-8')

    if '<ul>' in content:
        content = content.replace('<ul>\n', '<ul>\n' + entry + '\n', 1)
    else:
        content = content.replace(
            '\n        </main>',
            '\n            <hr />\n            <ul>\n' + entry + '\n            </ul>\n        </main>',
        )

    page_path.write_text(content, encoding='utf-8')


def main():
    print('=== Markdown 文章发布工具 ===\n')

    while True:
        raw = input('Markdown 文件路径: ').strip()
        md_path = Path(raw)
        if not md_path.is_absolute():
            md_path = ROOT_DIR / md_path
        if md_path.exists():
            break
        print(f'  文件不存在: {md_path}')

    text = md_path.read_text(encoding='utf-8')
    meta, body = parse_front_matter(text)

    title = ask('文章标题', meta.get('title', md_path.stem))
    date = ask('日期', meta.get('date', ''))

    print('\n分类:')
    for i, (key, name) in enumerate(CATEGORIES, 1):
        print(f'  {i}. {name} ({key})')
    while True:
        raw = input('分类编号 [1]: ').strip()
        idx = 0 if not raw else int(raw) - 1 if raw.isdigit() else -1
        if 0 <= idx < len(CATEGORIES):
            break
        print('  无效选择，请重试')
    category = CATEGORIES[idx][0]

    default_folder = slugify(meta.get('title', md_path.stem) or md_path.stem)
    folder = ask('文件夹命名', default_folder)

    output_path = ROOT_DIR / 'content' / category / folder / 'index.html'

    print()
    print('  标题: ' + title)
    print('  日期: ' + date)
    print('  分类: ' + category)
    print('  位置: ' + str(output_path.relative_to(ROOT_DIR)))

    confirm = input('\n是否继续? [Y/n]: ').strip().lower()
    if confirm == 'n':
        print('已取消')
        return

    template_str = TEMPLATE_PATH.read_text(encoding='utf-8')
    html_body = render_markdown(body)
    html_body = html_body.replace('<!--sep-->', '<br />')
    section = SECTION_MAP.get(category, '')
    result = fill_template(template_str, title, date, html_body, section)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding='utf-8')
    print('\n- 文章已生成: content/' + category + '/' + folder + '/index.html')

    if category in PAGE_MAP:
        add_entry_to_page(PAGE_MAP[category], title, date, category, folder)
        print('- 已添加到:   pages/' + category + '.html')
    else:
        print('- (分类 "' + category + '" 没有对应页面，跳过更新)')

    print('\n完成!')


if __name__ == '__main__':
    main()
