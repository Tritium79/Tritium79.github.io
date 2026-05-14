"""文章发布引擎：Markdown → HTML 的完整转换流水线。

流水线：读取 Markdown → 解析 front matter → 渲染 HTML →
       图片处理 → 填充 archetype.html 模板 → 写入 content/{cat}/{slug}/index.html
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from config import ROOT_DIR, ARCHETYPE_PATH, CATEGORIES, SECTION_MAP, PAGE_MAP
from utils import slugify, make_folder_name, ask, confirm, parse_front_matter, get_lunar_date
from management import add_entry_to_page
from data_loader import get_nav as get_nav_data, get_footer as get_footer_data, get_settings


# ── 自定义 Markdown 扩展：保留行首缩进 ───────────────────

_BLOCK_TAGS = frozenset({'p', 'li', 'blockquote', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th'})
_SKIP_TAGS = frozenset({'pre', 'code', 'kbd', 'samp'})


class _PreserveIndentTreeprocessor(Treeprocessor):
    def run(self, root):
        self._walk(root)

    def _walk(self, elem):
        if elem.tag in _SKIP_TAGS:
            return
        if elem.tag in _BLOCK_TAGS and elem.text:
            elem.text = self._nbsp_leading(elem.text)
        for child in elem:
            if child.tag not in _SKIP_TAGS and child.tail:
                child.tail = self._nbsp_leading(child.tail)
            self._walk(child)

    @staticmethod
    def _nbsp_leading(text):
        text = re.sub(r'(?<=\n) +', lambda m: '\u00A0' * len(m.group()), text)
        text = re.sub(r'^ +', lambda m: '\u00A0' * len(m.group()), text)
        return text


class _PreserveIndentExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_PreserveIndentTreeprocessor(md), 'preserve_indent', 15)


# ── 文本转换 ─────────────────────────────────────────────

def process_obsidian_links(text):
    return re.sub(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'![\1](\1)', text)


def process_links(html):
    enabled = get_settings('open_links_in_new_tab', True)
    if not enabled:
        return html
    return re.sub(r'<a\s+(?![^>]*target=)([^>]+?)>', r'<a \1 target="_blank">', html)


def render_markdown(text):
    text = process_obsidian_links(text)
    extensions = get_settings('markdown_extensions', ['extra', 'codehilite', 'nl2br'])
    return markdown.markdown(text, extensions=extensions + [_PreserveIndentExtension()])


# ── 图片处理 ─────────────────────────────────────────────

def process_images(html, md_path, output_dir):
    md_dir = md_path.parent
    copied = []

    def _replace_src(match):
        attrs = match.group(1)
        src = match.group(2)

        if src.startswith(('http://', 'https://', '//', 'data:')):
            return match.group(0)

        sp = Path(src)
        if not sp.is_absolute():
            sp = md_dir / src
        if not sp.exists():
            sp = ROOT_DIR / src
            if not sp.exists():
                print(f'  警告: 图片不存在: {src}')
                return match.group(0)

        fname = sp.name
        dest = output_dir / fname
        if sp.resolve() != dest.resolve():
            shutil.copy2(sp, dest)
            copied.append(fname)

        return f'<img {attrs.replace(src, fname).rstrip("/ ")}>'

    html = re.sub(r'<img\s+([^>]*src="([^"]+)"[^>]*)>', _replace_src, html, flags=re.IGNORECASE)
    return html, copied


def localize_md_images(text, md_path, output_dir):
    """将 Markdown 中的图片引用路径改为仅文件名，返回修改后的文本。"""
    md_dir = md_path.parent

    # 先转换 Obsidian 语法 ![[path]] → ![alt](path)
    text = re.sub(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'![\1](\1)', text)

    def _replace(match):
        alt = match.group(1)
        src = match.group(2)

        if src.startswith(('http://', 'https://', '//', 'data:')):
            return match.group(0)

        sp = Path(src)
        if not sp.is_absolute():
            sp = md_dir / src
        if not sp.exists():
            sp = ROOT_DIR / src
            if not sp.exists():
                return match.group(0)

        return f'![{alt}]({sp.name})'

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _replace, text)
    return text


# ── 模板渲染 ─────────────────────────────────────────────

def generate_nav_links(current_section_cn, prefix=''):
    items = get_nav_data()
    lines = []
    for href, cn, la in items:
        cls = 'nav-current' if cn == current_section_cn else ''
        path = prefix + href
        ac = f' class="{cls}"' if cls else ''
        lines.append(
            f'                <a href="{path}"{ac}>'
            f'<span class="nav-cn">{cn}</span>'
            f'<span class="sep">/</span>'
            f'<span class="nav-la">{la}</span>'
            f'</a>'
        )
    return '\n'.join(lines)


def fill_template(template, title, date, content, section):
    full_content = f'            <h2>{title}</h2>\n'
    full_content += f'            <p class="post-date">{date}</p>\n'
    full_content += content

    html = template
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ content }}', full_content)
    html = html.replace('{{ section }}', section)
    html = html.replace('{{ nav_links }}', generate_nav_links(section, '../../../'))
    html = html.replace('{{ footer_content }}', get_footer_data())
    html = html.replace('{{ root_path }}', '../../../')
    return html


# ── 发布流程 ─────────────────────────────────────────────

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
    raw_text = md_path.read_text(encoding='utf-8')
    meta, body = parse_front_matter(raw_text)

    title = args.title or (meta.get('title') if meta else md_path.stem)
    date = args.date or (meta.get('date') if meta else None)
    if not date:
        date = ask('日期', get_lunar_date())

    if is_cli_mode:
        if not args.category:
            print('错误: CLI 模式必须指定 --category')
            sys.exit(1)
        category = args.category
    else:
        category = select_category_interactive()

    if not is_cli_mode:
        title = ask('标题', title)
    folder = args.folder or make_folder_name(title, datetime.now())
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
        if not args.yes and confirm('是否覆盖?') != 'y':
            print('  已取消')
            return False
        print('  覆盖已存在的文章')

    if not args.yes and confirm('\n是否继续?') != 'y':
        print('  已取消')
        return False

    html_body = render_markdown(body)

    sep_marker = get_settings('separator_marker', '<!--sep-->')
    sep_replacement = get_settings('separator_replacement', '<br />')
    html_body = html_body.replace(sep_marker, sep_replacement)

    html_body = process_links(html_body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_body, copied = process_images(html_body, md_path, output_path.parent)

    section = SECTION_MAP.get(category, '')
    result = fill_template(ARCHETYPE_PATH.read_text(encoding='utf-8'),
                           title, date, html_body, section)

    output_path.write_text(result, encoding='utf-8')
    print(f'\n- 文章已生成: content/{category}/{folder}/index.html')

    md_localized = localize_md_images(raw_text, md_path, output_path.parent)
    (output_path.parent / 'index.md').write_text(md_localized, encoding='utf-8')
    print(f'  - 源文件已复制: content/{category}/{folder}/index.md')

    if copied:
        print(f'  已复制图片: {", ".join(copied)}')

    if category in PAGE_MAP:
        updated = add_entry_to_page(PAGE_MAP[category], title, date, category, folder)
        print(f'  {"已更新" if updated else "已添加到"}: pages/{category}.html')

    print('\n  完成!')
    return True
