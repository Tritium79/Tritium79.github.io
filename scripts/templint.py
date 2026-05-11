import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR


def _rel_path(file_path):
    return file_path.relative_to(ROOT_DIR).as_posix()


def _depth(file_path):
    return len(file_path.relative_to(ROOT_DIR).parent.parts)


def _prefix(depth):
    if depth == 0:
        return ''
    return '../' * depth


def _normalize_relative_paths(html, from_prefix='', to_prefix=''):
    return html.replace(from_prefix, to_prefix)


def _parse_shell(file_path):
    """Extract head content (before </head>) and body shell (header + footer) from an HTML file."""
    text = file_path.read_text(encoding='utf-8')
    head_match = re.search(r'<head>(.*?)</head>', text, re.DOTALL)
    body_match = re.search(r'<body>(.*?)</body>', text, re.DOTALL)
    head_content = head_match.group(1) if head_match else ''
    body_content = body_match.group(1) if body_match else ''
    main_match = re.search(r'<main>(.*?)</main>', text, re.DOTALL)
    main_content = main_match.group(1) if main_match else ''
    return head_content, body_content, main_content


def _extract_base_shell():
    base_path = ROOT_DIR / 'archetypes' / 'base.html'
    head, body, _ = _parse_shell(base_path)
    header_match = re.search(r'(.*?)<main>', body, re.DOTALL)
    footer_match = re.search(r'</main>(.*)', body, re.DOTALL)
    header_shell = header_match.group(1) if header_match else ''
    footer_shell = footer_match.group(1) if footer_match else ''
    footer_p_match = re.search(r'<p>(.*?)</p>', footer_shell, re.DOTALL)
    base_footer_text = re.sub(r'\s+', ' ', footer_p_match.group(1)).strip() if footer_p_match else ''
    nav_match = re.search(r'<nav>(.*?)</nav>', body, re.DOTALL)
    base_nav_html = nav_match.group(1).strip() if nav_match else ''
    return head, header_shell, footer_shell, base_footer_text, base_nav_html


def _base_nav_links():
    return [
        ('首页', 'Domus'),
        ('随笔', 'Sylvae'),
        ('记录', 'Commentarii'),
        ('译文', 'Interpretationes'),
        ('存档', 'Tabularium'),
        ('友链', 'Amici'),
        ('关于', 'De Me'),
    ]


def _find_html_files():
    files = []
    # root html
    for f in ROOT_DIR.glob('*.html'):
        if f.name != 'base.html':
            files.append(f)
    # pages/
    pages_dir = ROOT_DIR / 'pages'
    if pages_dir.exists():
        for f in pages_dir.glob('*.html'):
            files.append(f)
    # content/**/index.html
    content_dir = ROOT_DIR / 'content'
    if content_dir.exists():
        for f in content_dir.rglob('index.html'):
            files.append(f)
    # archetypes/article.html
    article_tpl = ROOT_DIR / 'archetypes' / 'article.html'
    if article_tpl.exists():
        files.append(article_tpl)
    return sorted(set(files))


def check_file(file_path, base_head, base_header_shell, base_footer_shell, base_footer_text, base_nav_html):
    issues = []
    text = file_path.read_text(encoding='utf-8')

    if not text.startswith('<!doctype html>'):
        issues.append('缺 <!doctype html>')

    if '<html lang="zh-CN">' not in text:
        issues.append('<html> 缺 lang="zh-CN"')

    head_match = re.search(r'<head>(.*?)</head>', text, re.DOTALL)
    if not head_match:
        issues.append('缺 <head>')
    else:
        head_content = head_match.group(1)
        if '<meta charset="UTF-8"' not in head_content:
            issues.append('缺 charset meta')
        if '<meta name="viewport"' not in head_content:
            issues.append('缺 viewport meta')
        if 'style.css' not in head_content:
            issues.append('缺 style.css 链接')
        title_match = re.search(r'<title>(.*?)</title>', head_content, re.DOTALL)
        if not title_match:
            issues.append('缺 <title>')
        else:
            title_text = re.sub(r'\s+', ' ', title_match.group(1)).strip()
            if '| Tritium79\'s Blog' not in title_text:
                issues.append('title 格式不符（应含 "| Tritium79\'s Blog"）')

    if not re.search(r'<header>.*?</header>', text, re.DOTALL):
        issues.append('缺 <header>')
    else:
        header_match = re.search(r'<header>(.*?)</header>', text, re.DOTALL)
        header_content = header_match.group(1) if header_match else ''
        if 'avatar.png' not in header_content:
            issues.append('header 缺头像')
        if 'Tritium79\'s Blog' not in header_content:
            issues.append('header 缺博客标题')
        if 'nav-toggle' not in header_content:
            issues.append('header 缺导航切换按钮')

        nav_match = re.search(r'<nav>(.*?)</nav>', header_content, re.DOTALL)
        if not nav_match:
            issues.append('缺 <nav>')
        elif '{{ nav_links }}' in nav_match.group(1):
            pass  # dynamically generated nav, skip comparison
        else:
            def _nav_entries(html):
                entries = []
                for a_tag in re.findall(r'<a[^>]*>.*?</a\s*>', html, re.DOTALL):
                    href = re.search(r'href="([^"]+)"', a_tag)
                    label = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', a_tag))
                    if href:
                        fname = Path(href.group(1)).name
                        entries.append((fname, label))
                return entries
            file_entries = _nav_entries(nav_match.group(1))
            base_entries = _nav_entries(base_nav_html)
            file_map = dict(file_entries)
            base_map = dict(base_entries)
            if file_map.keys() != base_map.keys():
                missing = set(base_map) - set(file_map)
                extra = set(file_map) - set(base_map)
                msg = '导航链接目标不符'
                if missing: msg += f'，缺: {", ".join(sorted(missing))}'
                if extra: msg += f'，多余: {", ".join(sorted(extra))}'
                issues.append(msg)
            for key in file_map:
                if key in base_map and file_map[key] != base_map[key]:
                    issues.append(f'导航链接 "{key}" 文字不符（应为 "{base_map[key]}"）')

    if not re.search(r'<main>.*?</main>', text, re.DOTALL):
        issues.append('缺 <main>')

    if not re.search(r'<footer>.*?</footer>', text, re.DOTALL):
        issues.append('缺 <footer>')
    else:
        footer_match = re.search(r'<footer>(.*?)</footer>', text, re.DOTALL)
        footer_content = footer_match.group(1) if footer_match else ''
        file_footer_p = re.search(r'<p>(.*?)</p>', footer_content, re.DOTALL)
        file_footer_text = re.sub(r'\s+', ' ', file_footer_p.group(1)).strip() if file_footer_p else ''
        if file_footer_text != base_footer_text:
            issues.append(f'footer 内容不符（期望 "{base_footer_text}"，实际 "{file_footer_text}"）')

    return issues


def rebuild_from_base(file_path):
    """Rebuild the HTML file based on base.html, preserving <main> content and extra <head> items."""
    depth = _depth(file_path)
    pref = _prefix(depth)

    _, _, main_content = _parse_shell(file_path)
    main_content = main_content.strip()

    # preserve extra head content (beyond base.html's head)
    orig_head, _, _ = _parse_shell(file_path)
    extra_head = ''
    base_head_base, _, _ = _parse_shell(ROOT_DIR / 'template' / 'base.html')
    # extract what's in orig_head but not in base_head_base (like KaTeX)
    # simple approach: remove standard elements and keep the rest
    standard_items = [
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        '<link rel="stylesheet" href="/style.css" />',
    ]
    remaining = orig_head
    for item in standard_items:
        remaining = remaining.replace(item, '')
    remaining = re.sub(r'<title>.*?</title>', '', remaining, flags=re.DOTALL).strip()
    if remaining:
        extra_head = '\n' + remaining

    # rebuild shell from base.html with adjusted paths
    base_path = ROOT_DIR / 'archetypes' / 'base.html'
    base_text = base_path.read_text(encoding='utf-8')

    # convert root-relative paths to depth-appropriate relative paths
    base_text = base_text.replace('href="/', f'href="{pref}')
    base_text = base_text.replace('src="/', f'src="{pref}')

    # insert extra head content
    if extra_head:
        base_text = base_text.replace('</head>', extra_head + '\n    </head>')

    # find title placeholder and content in rebuilt text
    title_match = re.search(r'<title>(.*?)\s*\| Tritium79\'s Blog</title>', file_path.read_text(encoding='utf-8'), re.DOTALL)
    title = title_match.group(1) if title_match else ''

    # replace placeholder
    base_text = base_text.replace('{{ title }}', title)
    base_text = base_text.replace('{{ content }}', main_content)

    # clean up any remaining placeholders
    base_text = base_text.replace('{{ title }}', '')
    base_text = base_text.replace('{{ content }}', '')

    return base_text


def check_all(interactive=True, yes_to_all=False):
    base_head, base_header_shell, base_footer_shell, base_footer_text, base_nav_html = _extract_base_shell()
    html_files = _find_html_files()

    print(f'检查 {len(html_files)} 个 HTML 文件与 archetypes/base.html 的结构一致性...\n')

    total_issues = 0
    fixable_files = []

    for f in html_files:
        rel = _rel_path(f)
        issues = check_file(f, base_head, base_header_shell, base_footer_shell, base_footer_text, base_nav_html)
        if issues:
            total_issues += len(issues)
            print(f'  ✗ {rel}')
            for issue in issues:
                print(f'      - {issue}')
            fixable_files.append(f)
        else:
            print(f'  ✓ {rel}')

    print(f'\n总计: {len(html_files)} 个文件, {len(fixable_files)} 个有问题, {total_issues} 项差异')

    if fixable_files:
        if yes_to_all:
            for f in fixable_files:
                rel = _rel_path(f)
                new_content = rebuild_from_base(f)
                f.write_text(new_content, encoding='utf-8')
                print(f'  已更新: {rel}')
        elif interactive:
            for f in fixable_files:
                rel = _rel_path(f)
                print(f'\n── {rel} ──')
                print('是否按照 base.html 模板重建此文件？')
                choice = input('[y/n]: ').strip().lower()
                if choice in ('y', ''):
                    new_content = rebuild_from_base(f)
                    f.write_text(new_content, encoding='utf-8')
                    print(f'  已更新: {rel}')
                else:
                    print(f'  已跳过: {rel}')

    return len(fixable_files) == 0
