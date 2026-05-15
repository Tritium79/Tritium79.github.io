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

import xml.etree.ElementTree as etree
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from config import ROOT_DIR, ARCHETYPE_PATH, CATEGORIES, SECTION_MAP, PAGE_MAP
from utils import slugify, make_folder_name, ask, confirm, parse_front_matter, get_lunar_date
from management import add_entry_to_page
from data_loader import get_nav as get_nav_data, get_footer as get_footer_data, get_settings


# ── 自定义 Markdown 扩展：任务列表 ───────────────────────

_TASK_RE = re.compile(r'^\s*\[( |x|X)\]\s+')


class _TasklistTreeprocessor(Treeprocessor):
    def run(self, root):
        for li in root.iter('li'):
            if li.text and _TASK_RE.match(li.text):
                m = _TASK_RE.match(li.text)
                checked = m.group(1) in ('x', 'X')
                cb = etree.SubElement(li, 'input',
                                      {'type': 'checkbox', 'disabled': ''})
                if checked:
                    cb.set('checked', '')
                cb.tail = li.text[m.end():]
                li.text = ''


class _TasklistExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_TasklistTreeprocessor(md), 'tasklist', 10)


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


# ── 自定义 Markdown 扩展：嵌套有序列表 start 属性 ────────

class _NestedOListTreeprocessor(Treeprocessor):
    def run(self, root):
        self._walk(root, None, 0)

    def _walk(self, elem, parent_ol, parent_li_idx):
        if elem.tag == 'ol':
            parent_start = int(elem.get('start', 1))
            li_idx = 0
            for child in list(elem):
                if child.tag == 'li':
                    li_idx += 1
                    self._walk(child, elem, li_idx)
                else:
                    self._walk(child, None, 0)
        elif elem.tag == 'li':
            for child in list(elem):
                if child.tag == 'ol' and parent_ol is not None:
                    ps = int(parent_ol.get('start', 1))
                    child.set('start', str(ps + parent_li_idx))
                self._walk(child, parent_ol, parent_li_idx)
        else:
            for child in list(elem):
                self._walk(child, parent_ol, parent_li_idx)


class _NestedOListExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_NestedOListTreeprocessor(md), 'nested_olist', 20)


# ── 文本预处理：删除线、高亮、上标、下标 ─────────────────

_STRIKE_RE = re.compile(r'~~(.+?)~~')
_HIGHLIGHT_RE = re.compile(r'==(.+?)==')
_SUP_RE = re.compile(r'\^(.+?)\^')
_SUB_RE = re.compile(r'(?<!\~)~(?!~)(.+?)(?<!\~)~(?!~)')


def ensure_blank_line_before_lists(text):
    lines = text.split('\n')
    result = []
    in_code = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
        if i > 0 and not in_code and stripped:
            prev = lines[i - 1].strip()
            is_list = bool(re.match(r'^[ \t]*[-*+]\s', line)) or bool(re.match(r'^[ \t]*\d+[.)]\s', line))
            if prev and is_list:
                prev_is_list = bool(re.match(r'^[ \t]*[-*+]\s', lines[i - 1])) or bool(
                    re.match(r'^[ \t]*\d+[.)]\s', lines[i - 1])
                )
                if not prev_is_list:
                    result.append('')
        result.append(line)
    return '\n'.join(result)


def preprocess_inline(text):
    text = _STRIKE_RE.sub(r'<del>\1</del>', text)
    text = _HIGHLIGHT_RE.sub(r'<mark>\1</mark>', text)
    text = _SUP_RE.sub(r'<sup>\1</sup>', text)
    text = _SUB_RE.sub(r'<sub>\1</sub>', text)
    return text


# ── 文本转换 ─────────────────────────────────────────────

def process_obsidian_links(text):
    return re.sub(r'!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'![\1](\1)', text)


def process_links(html):
    enabled = get_settings('open_links_in_new_tab', True)
    if not enabled:
        return html
    return re.sub(r'<a\s+(?![^>]*target=)(?![^>]*class="footnote-(?:ref|backref)")([^>]+?)>', r'<a \1 target="_blank">', html)


def _protect_math(text):
    placeholders = {}

    def _save(m):
        key = f'\x00MATH_{len(placeholders)}\x00'
        placeholders[key] = m.group(0)
        return key

    text = re.sub(r'\$\$(.*?)\$\$', _save, text, flags=re.DOTALL)
    text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _save, text)
    text = re.sub(r'\\\[(.*?)\\\]', _save, text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', _save, text, flags=re.DOTALL)

    return text, placeholders


def render_markdown(text):
    text = process_obsidian_links(text)
    text, math_blocks = _protect_math(text)
    text = preprocess_inline(text)
    text = ensure_blank_line_before_lists(text)
    extensions = get_settings('markdown_extensions', ['extra', 'codehilite', 'nl2br'])
    md = markdown.Markdown(
        extensions=extensions + [_PreserveIndentExtension(), _TasklistExtension(), _NestedOListExtension()],
        tab_length=2
    )
    html = md.convert(text)
    for key, val in math_blocks.items():
        html = html.replace(key, val)
    return html


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


# ── KaTeX 条件引入 ────────────────────────────────────────

KATEX_HTML = r'''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.46/dist/katex.min.css" />

        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.46/dist/katex.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.46/dist/contrib/auto-render.min.js"></script>
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.46/dist/contrib/mhchem.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                renderMathInElement(document.body, {
                    delimiters: [
                        {left: "$$", right: "$$", display: true},
                        {left: "$", right: "$", display: false},
                        {left: "\\(", right: "\\)", display: false},
                        {left: "\\[", right: "\\]", display: true}
                    ],
                    throwOnError: false,
                    trust: true,
                    macros: {
                        "\\f": "#1f(#2)"
                    }
                });
            });
        </script>

        <style>
        .katex-display { overflow: visible !important; }
        .katex-display > .katex { overflow: visible !important; }
        .katex { overflow: visible !important; }
        </style>'''


# ── Obsidian Callout 处理 ──────────────────────────────────

def _callout_div(type_, title, content):
    title_html = f'<div class="callout-title">{title}</div>' if title else ''
    return (
        f'<div class="callout callout-{type_}">'
        f'{title_html}'
        f'<div class="callout-content">\n{content}\n</div></div>'
    )


def _parse_callout_p(p_html):
    """Parse a <p>[!type] title<br />body</p> segment into (type, title, body) or None."""
    m = re.match(r'<p>\[!(\w+)\]\s*(.*)', p_html, re.DOTALL)
    if not m:
        return None
    type_ = m.group(1).lower()
    rest = m.group(2).strip()
    # Remove closing </p> if present
    if rest.endswith('</p>'):
        rest = rest[:-4].rstrip()
    parts = re.split(r'<br\s*/?>\s*\n?', rest, maxsplit=1)
    title = parts[0].strip()
    body = parts[1].strip() if len(parts) > 1 else ''
    return (type_, title, body)


def process_callouts(html):
    result = []
    pos = 0
    while pos < len(html):
        bq_start = html.find('<blockquote>', pos)
        if bq_start == -1:
            result.append(html[pos:])
            break
        result.append(html[pos:bq_start])
        bq_end = html.find('</blockquote>', bq_start)
        if bq_end == -1:
            result.append(html[bq_start:])
            break

        inner = html[bq_start + len('<blockquote>'):bq_end]

        if '[!' not in inner:
            result.append(html[bq_start:bq_end + len('</blockquote>')])
            pos = bq_end + len('</blockquote>')
            continue

        # Split inner at <p>[!type] boundaries (keep delimiter in segment)
        segments = re.split(r'(?=<p>\[!\w+\])', inner)
        processed = []
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            callout = _parse_callout_p(seg)
            if callout:
                processed.append(_callout_div(*callout))
            else:
                processed.append(f'<blockquote>\n{seg}\n</blockquote>')

        result.append('\n'.join(processed))
        pos = bq_end + len('</blockquote>')

    return ''.join(result)


def has_latex(html):
    """Check if HTML body contains LaTeX math delimiters ($$, \\[, \\()."""
    return '$$' in html or '\\[' in html or '\\(' in html


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
    full_content = f'            <h2 class="article-title">{title}</h2>\n'
    full_content += f'            <p class="post-date">{date}</p>\n'
    full_content += content

    katex_html = KATEX_HTML if has_latex(content) else ''

    html = template
    html = html.replace('{{ title }}', title)
    html = html.replace('{{ content }}', full_content)
    html = html.replace('{{ section }}', section)
    html = html.replace('{{ nav_links }}', generate_nav_links(section, '../../../'))
    html = html.replace('{{ footer_content }}', get_footer_data())
    html = html.replace('{{ root_path }}', '../../../')
    html = html.replace('{{ katex }}', katex_html)
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

    html_body = process_callouts(html_body)

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
