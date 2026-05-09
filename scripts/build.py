#!/usr/bin/env python3
"""交互式将 Markdown 文章转换为独立 HTML 页面，并自动更新对应分类页。

支持非交互式模式：
    python build.py --file article.md --category silvae [--title "标题"] [--date "日期"] [--folder folder-name]
"""

import argparse
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

ENTRY_PATTERN = re.compile(
    r'(<li>\s*<a\s+href="../content/' + r'([^"]+)' + r'/index.html"[^>]*>)' + r'.*?</a>\s*<p class="article-date">\s*(.*?)\s*</p>\s*</li>',
    re.DOTALL
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
    return markdown.markdown(text, extensions=['extra', 'codehilite'])


def process_latex(html):
    inline_pattern = re.compile(r'(?<!\$)\$(?!\$)([^\$\n]+)\$(?!\$)')
    block_pattern = re.compile(r'\$\$([\s\S]+?)\$\$')

    html = block_pattern.sub(r'<div class="arithmatex">$$\1$$</div>', html)
    html = inline_pattern.sub(r'<span class="arithmatex">\(\1\)</span>', html)

    return html


def process_images(html, md_path, output_dir):
    import shutil

    md_dir = md_path.parent

    image_pattern = re.compile(r'<img\s+src="([^"]+)"\s+([^>]*)>', re.IGNORECASE)

    copied_images = []

    def replace_src(match):
        src = match.group(1)
        attrs = match.group(2)

        if src.startswith(('http://', 'https://', '//', 'data:')):
            return match.group(0)

        src_path = md_dir / src
        if not src_path.exists():
            src_path = ROOT_DIR / src
            if not src_path.exists():
                print(f'  警告: 图片不存在: {src}')
                return match.group(0)

        filename = Path(src).name
        dest_path = output_dir / filename

        if src_path.resolve() != dest_path.resolve():
            shutil.copy2(src_path, dest_path)
            copied_images.append(filename)

        return f'<img src="{filename}" {attrs}>'

    html = image_pattern.sub(replace_src, html)
    return html, copied_images


def fill_template(template, title, date, content, section):
    html = template
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ date }}', date)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ section }}', section)
    return html


def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\u4e00-\u9fff-]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    words = text.split('-')
    def capitalize_word(word):
        if word.isupper():
            return word
        return word.capitalize()
    return '-'.join(capitalize_word(word) for word in words if word)


def ask(prompt, default=None):
    if default is not None:
        raw = input(f'{prompt} [{default}]: ').strip()
        return raw if raw else default
    return input(f'{prompt}: ').strip()


def confirm(prompt, default='n'):
    default_y = 'Y' if default == 'y' else 'n'
    raw = input(f'{prompt} [{default_y}]: ').strip().lower()
    return raw if raw else default


def add_entry_to_page(page_path, title, date, category, folder):
    if not page_path.exists():
        return False

    entry = (ENTRY_TPL
             .replace('%%CATEGORY%%', category)
             .replace('%%FOLDER%%', folder)
             .replace('%%TITLE%%', title)
             .replace('%%DATE%%', date))

    content = page_path.read_text(encoding='utf-8')

    pattern = re.compile(
        r'(<li>\s*<a\s+href="../content/' + re.escape(category) + r'/' + re.escape(folder) + r'/index.html"[^>]*>)',
        re.DOTALL
    )
    match = pattern.search(content)

    if match:
        start = match.start()
        end_pattern = re.compile(r'</li>')
        end_match = end_pattern.search(content, start)
        if end_match:
            end = end_match.end()
            old_entry = content[start:end]
            content = content[:start] + entry.strip() + content[end:]
            page_path.write_text(content, encoding='utf-8')
            return True

    if '<ul>' in content:
        content = content.replace('<ul>\n', '<ul>\n' + entry + '\n', 1)
    else:
        content = content.replace(
            '\n        </main>',
            '\n            <hr />\n            <ul>\n' + entry + '\n            </ul>\n        </main>',
        )

    page_path.write_text(content, encoding='utf-8')
    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description='将 Markdown 文章转换为独立 HTML 页面',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python build.py                           # 交互模式
  python build.py --file article.md         # 指定文件，使用交互选择分类
  python build.py --file article.md --category silvae  # 完全非交互
  python build.py -f article.md -c silvae -t "标题" -d "2024-01-01"
        '''
    )
    parser.add_argument('-f', '--file', type=str, help='Markdown 文件路径')
    parser.add_argument('-c', '--category', type=str, choices=[c[0] for c in CATEGORIES],
                        help='分类 (silvae/commentarii/versiones/archivum)')
    parser.add_argument('-t', '--title', type=str, help='文章标题 (默认从 front matter 或文件名读取)')
    parser.add_argument('-d', '--date', type=str, help='发布日期 (默认从 front matter 读取)')
    parser.add_argument('--folder', type=str, help='文章文件夹名 (默认从标题自动生成)')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='跳过确认步骤，直接执行')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.file:
        md_path = Path(args.file)
        if not md_path.is_absolute():
            md_path = ROOT_DIR / md_path
        if not md_path.exists():
            print(f"错误: 文件不存在: {md_path}")
            sys.exit(1)
    else:
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

    if args.file:
        is_cli_mode = True
    else:
        is_cli_mode = False

    title = args.title if args.title else (meta.get('title') if meta else md_path.stem)

    date = args.date if args.date else (meta.get('date') if meta else None)
    if not date:
        date = ask('日期', '')

    if is_cli_mode and args.category:
        category = args.category
    elif is_cli_mode:
        print('\n错误: CLI 模式必须指定 --category')
        sys.exit(1)
    else:
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

    default_folder = slugify(meta.get('title', md_path.stem) if meta else md_path.stem) if meta else slugify(md_path.stem)
    folder = args.folder if args.folder else (ask('文件夹命名', default_folder) if not is_cli_mode else default_folder)

    output_path = ROOT_DIR / 'content' / category / folder / 'index.html'

    print()
    print(f'  标题: {title}')
    print(f'  日期: {date}')
    print(f'  分类: {category}')
    print(f'  位置: {output_path.relative_to(ROOT_DIR)}')

    if output_path.parent.exists():
        print(f'\n警告: 目标文件夹已存在: content/{category}/{folder}/')
        if not args.yes:
            if confirm('是否覆盖?') != 'y':
                print('已取消')
                return
        print('  覆盖已存在的文章')

    if not args.yes and not is_cli_mode:
        confirm_step = input('\n是否继续? [Y/n]: ').strip().lower()
        if confirm_step == 'n':
            print('已取消')
            return
    elif not args.yes and is_cli_mode:
        if confirm('\n是否继续?') != 'y':
            print('已取消')
            return

    template_str = TEMPLATE_PATH.read_text(encoding='utf-8')
    html_body = render_markdown(body)
    html_body = html_body.replace('<!--sep-->', '<br />')
    html_body = process_latex(html_body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_body, copied_images = process_images(html_body, md_path, output_path.parent)

    section = SECTION_MAP.get(category, '')
    result = fill_template(template_str, title, date, html_body, section)

    output_path.write_text(result, encoding='utf-8')
    print(f'\n- 文章已生成: content/{category}/{folder}/index.html')
    if copied_images:
        print(f'- 已复制图片: {", ".join(copied_images)}')

    if category in PAGE_MAP:
        updated = add_entry_to_page(PAGE_MAP[category], title, date, category, folder)
        if updated:
            print(f'- 已更新:     pages/{category}.html')
        else:
            print(f'- 已添加到:   pages/{category}.html')
    else:
        print(f'- (分类 "{category}" 没有对应页面，跳过更新)')

    print('\n完成!')


if __name__ == '__main__':
    main()