import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import markdown

from config import ROOT_DIR, TEMPLATE_PATH, CATEGORIES, SECTION_MAP, PAGE_MAP
from utils import slugify, ask, confirm, parse_front_matter, get_lunar_date
from management import add_entry_to_page


def process_obsidian_links(text):
    wiki_image_pattern = re.compile(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
    return wiki_image_pattern.sub(r'![\1](\1)', text)


def process_links(html):
    return re.sub(r'<a\s+(?![^>]*target=)([^>]+?)>',
                  r'<a \1 target="_blank">', html)

def render_markdown(text):
    text = process_obsidian_links(text)
    return markdown.markdown(text, extensions=['extra', 'codehilite', 'nl2br'])


def process_images(html, md_path, output_dir):
    md_dir = md_path.parent
    image_pattern = re.compile(r'<img\s+([^>]*src="([^"]+)"[^>]*)>', re.IGNORECASE)
    copied_images = []

    def replace_src(match):
        full_attrs = match.group(1)
        src = match.group(2)

        if src.startswith(('http://', 'https://', '//', 'data:')):
            return match.group(0)

        src_path = Path(src)
        if not src_path.is_absolute():
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

        new_attrs = full_attrs.replace(src, filename).rstrip('/ ')
        return f'<img {new_attrs}>'

    html = image_pattern.sub(replace_src, html)
    return html, copied_images


NAV_ITEMS = [
    ('index.html', '首页', 'Domus'),
    ('pages/sylvae.html', '随笔', 'Sylvae'),
    ('pages/commentarii.html', '记录', 'Commentarii'),
    ('pages/interpretationes.html', '译文', 'Interpretationes'),
    ('pages/tabularium.html', '存档', 'Tabularium'),
    ('pages/amici.html', '友链', 'Amici'),
    ('pages/deme.html', '关于', 'De Me'),
]


def generate_nav_links(current_section_cn, prefix=''):
    links = []
    for href, cn, la in NAV_ITEMS:
        cls = 'nav-current' if cn == current_section_cn else ''
        path = prefix + href
        attrs = f' class="{cls}"' if cls else ''
        links.append(
            f'                <a href="{path}"{attrs}><span class="nav-cn">{cn}</span><span class="sep">/</span><span class="nav-la">{la}</span></a>'
        )
    return '\n'.join(links)


def fill_template(template, title, date, content, section):
    html = template
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ date }}', date)
    html = html.replace('{{ content }}', content)
    html = html.replace('{{ section }}', section)
    # generate nav links with article's depth prefix (../../../)
    nav_html = generate_nav_links(section, '../../../')
    html = html.replace('{{ nav_links }}', nav_html)
    return html


def select_category_interactive():
    print('分类:')
    for i, (key, name) in enumerate(CATEGORIES, 1):
        print(f'  {i}. {name} ({key})')
    while True:
        raw = input('分类编号 [1]: ').strip()
        idx = 0 if not raw else int(raw) - 1 if raw.isdigit() else -1
        if 0 <= idx < len(CATEGORIES):
            return CATEGORIES[idx][0]
        print('  无效选择，请重试')


def publish_article(md_path, args, is_cli_mode):
    text = md_path.read_text(encoding='utf-8')
    meta, body = parse_front_matter(text)

    title = args.title if args.title else (meta.get('title') if meta else md_path.stem)
    date = args.date if args.date else (meta.get('date') if meta else None)
    if not date:
        date = ask('日期', get_lunar_date())

    if is_cli_mode and args.category:
        category = args.category
    elif is_cli_mode:
        print('错误: CLI 模式必须指定 --category')
        sys.exit(1)
    else:
        category = select_category_interactive()

    if not is_cli_mode:
        title = ask('标题', title)

    default_folder = slugify(title)
    folder = args.folder if args.folder else default_folder
    if not is_cli_mode:
        folder = ask('文件夹命名', folder)

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
                print('  已取消')
                return False
        print('  覆盖已存在的文章')

    if not args.yes:
        if confirm('\n是否继续?') != 'y':
            print('  已取消')
            return False

    template_str = TEMPLATE_PATH.read_text(encoding='utf-8')
    html_body = render_markdown(body)
    html_body = html_body.replace('<!--sep-->', '<br />')
    html_body = process_links(html_body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_body, copied_images = process_images(html_body, md_path, output_path.parent)

    section = SECTION_MAP.get(category, '')
    result = fill_template(template_str, title, date, html_body, section)

    output_path.write_text(result, encoding='utf-8')
    print(f'\n- 文章已生成: content/{category}/{folder}/index.html')
    if copied_images:
        print(f'  已复制图片: {", ".join(copied_images)}')

    if category in PAGE_MAP:
        updated = add_entry_to_page(PAGE_MAP[category], title, date, category, folder)
        status = '已更新' if updated else '已添加到'
        print(f'  {status}: pages/{category}.html')

    print('\n  完成!')
    return True
