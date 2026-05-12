"""模板一致性检查与全站 Shell 同步引擎。

核心功能：
    1. check_file() —— 对照 data/config.json 检查单个 HTML 文件的结构完整性
    2. check_all()  —— 扫描全站 HTML，逐个检查和交互式/自动修复
    3. rebuild_from_base() —— 提取文件的 <main> 内容，用当前 archetype.html 模板重包裹
    4. rebuild_all() —— 非交互式全站 Shell 同步
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR, SECTION_MAP
from content import generate_nav_links
from data_loader import (
    get_nav as get_nav_data,
    get_footer as get_footer_data,
    get_site_title,
    get_html_lang,
    get_avatar,
    get_css_file,
)


# ── 路径工具 ──────────────────────────────────────────────

def _rel_path(file_path):
    return file_path.relative_to(ROOT_DIR).as_posix()


def _depth(file_path):
    return len(file_path.relative_to(ROOT_DIR).parent.parts)


def _prefix(depth):
    return '' if depth == 0 else '../' * depth


# ── HTML 解析 ─────────────────────────────────────────────

def _parse_head_body_main(file_path):
    text = file_path.read_text(encoding='utf-8')
    h = re.search(r'<head>(.*?)</head>', text, re.DOTALL)
    b = re.search(r'<body>(.*?)</body>', text, re.DOTALL)
    m = re.search(r'<main>(.*?)</main>', text, re.DOTALL)
    return (
        h.group(1) if h else '',
        b.group(1) if b else '',
        m.group(1) if m else '',
    )


def _get_title_from_head(head_content):
    title_suffix = f'| {get_site_title()}'
    m = re.search(rf'<title>(.*?)\s*{re.escape(title_suffix)}', head_content)
    return m.group(1).strip() if m else ''


def _extract_extra_head(head_content):
    std = [
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
    ]
    rest = head_content
    for s in std:
        rest = rest.replace(s, '')
    css_file = get_css_file()
    rest = re.sub(rf'<link[^>]*{re.escape(css_file)}[^>]*/?>', '', rest)
    rest = re.sub(r'<title>.*?</title>', '', rest, flags=re.DOTALL)
    rest = rest.strip()
    return '\n' + rest if rest else ''


# ── 导航比较 ─────────────────────────────────────────────

def _extract_nav_entries(html):
    entries = []
    nav = re.search(r'<nav>(.*?)</nav>', html, re.DOTALL)
    if not nav:
        return entries
    for a in re.findall(r'<a[^>]*>.*?</a\s*>', nav.group(1), re.DOTALL):
        href = re.search(r'href="([^"]+)"', a)
        label = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', a))
        if href:
            entries.append((Path(href.group(1)).name, label))
    return entries


def _get_expected_nav_entries():
    return [
        (Path(href).name, re.sub(r'\s+', '', f'{cn}/{la}'))
        for href, cn, la in get_nav_data()
    ]


def _get_section_from_path(file_path):
    rel = _rel_path(file_path)
    for href, cn, _ in get_nav_data():
        if rel == href:
            return cn
    parts = Path(rel).parts
    if len(parts) >= 2 and parts[1] in SECTION_MAP:
        return SECTION_MAP[parts[1]]
    return ''


# ── 文件检查 ─────────────────────────────────────────────

def check_file(file_path):
    issues = []
    text = file_path.read_text(encoding='utf-8')

    html_lang = get_html_lang()
    site_title = get_site_title()
    avatar = get_avatar()
    css_file = get_css_file()

    if not text.startswith('<!doctype html>'):
        issues.append('缺 <!doctype html>')
    if f'<html lang="{html_lang}">' not in text:
        issues.append(f'<html> 缺 lang="{html_lang}"')

    h = re.search(r'<head>(.*?)</head>', text, re.DOTALL)
    if not h:
        issues.append('缺 <head>')
    else:
        hc = h.group(1)
        if '<meta charset="UTF-8"' not in hc:
            issues.append('缺 charset meta')
        if '<meta name="viewport"' not in hc:
            issues.append('缺 viewport meta')
        if css_file not in hc:
            issues.append(f'缺 {css_file} 链接')
        tm = re.search(r'<title>(.*?)</title>', hc, re.DOTALL)
        if not tm:
            issues.append('缺 <title>')
        elif f'| {site_title}' not in re.sub(r'\s+', ' ', tm.group(1)).strip():
            issues.append(f'title 格式不符（应含 "| {site_title}"）')

    hdr = re.search(r'<header>(.*?)</header>', text, re.DOTALL)
    if not hdr:
        issues.append('缺 <header>')
    else:
        hc = hdr.group(1)
        if avatar not in hc:
            issues.append(f'header 缺头像（{avatar}）')
        if site_title not in hc:
            issues.append(f'header 缺博客标题（{site_title}）')
        if 'nav-toggle' not in hc:
            issues.append('header 缺导航切换按钮')

        nav = re.search(r'<nav>(.*?)</nav>', hc, re.DOTALL)
        if not nav:
            issues.append('缺 <nav>')
        elif '{{ nav_links }}' not in nav.group(1):
            actual = _extract_nav_entries(text)
            expected = _get_expected_nav_entries()
            am, em = dict(actual), dict(expected)
            if am.keys() != em.keys():
                diff = set(em) - set(am)
                extra = set(am) - set(em)
                msg = '导航链接目标不符'
                if diff:
                    msg += f'，缺: {", ".join(sorted(diff))}'
                if extra:
                    msg += f'，多余: {", ".join(sorted(extra))}'
                issues.append(msg)
            for k in am:
                if k in em and am[k] != em[k]:
                    issues.append(f'导航链接 "{k}" 文字不符（应为 "{em[k]}"）')

    if not re.search(r'<main>.*?</main>', text, re.DOTALL):
        issues.append('缺 <main>')

    ft = re.search(r'<footer>(.*?)</footer>', text, re.DOTALL)
    if not ft:
        issues.append('缺 <footer>')
    else:
        fc = ft.group(1)
        if '{{ footer_content }}' in fc:
            pass
        else:
            actual = re.sub(r'\s+', ' ', fc.strip())
            expected = re.sub(r'\s+', ' ', f'<p>{get_footer_data()}</p>')
            if actual != expected:
                issues.append('footer 内容不符')

    return issues


# ── 文件重建 ─────────────────────────────────────────────

def rebuild_from_base(file_path):
    depth = _depth(file_path)
    pref = _prefix(depth)
    section = _get_section_from_path(file_path)

    head, _, main = _parse_head_body_main(file_path)
    title = _get_title_from_head(head)

    template = (ROOT_DIR / 'archetypes' / 'archetype.html').read_text(encoding='utf-8')

    out = template
    out = out.replace('{{ title }}', title)
    out = out.replace('{{ section }}', section)
    out = out.replace('{{ content }}', main.strip())
    out = out.replace('{{ nav_links }}', generate_nav_links(section, pref))
    out = out.replace('{{ footer_content }}', get_footer_data())
    out = out.replace('{{ root_path }}', pref)

    return out


# ── 全站扫描 ─────────────────────────────────────────────

def _find_html_files():
    files = []
    for f in ROOT_DIR.glob('*.html'):
        if f.name not in ('archetype.html',):
            files.append(f)
    pd = ROOT_DIR / 'pages'
    if pd.exists():
        files.extend(pd.glob('*.html'))
    cd = ROOT_DIR / 'content'
    if cd.exists():
        files.extend(cd.rglob('index.html'))
    tp = ROOT_DIR / 'archetypes' / 'archetype.html'
    if tp.exists():
        files.append(tp)
    return sorted(set(files))


def check_all(interactive=True, yes_to_all=False):
    files = _find_html_files()
    print(f'检查 {len(files)} 个 HTML 文件与模板的结构一致性...\n')

    issues_total = 0
    fixable = []

    for f in files:
        rel = _rel_path(f)
        iss = check_file(f)
        if iss:
            issues_total += len(iss)
            print(f'  \u2717 {rel}')
            for i in iss:
                print(f'      - {i}')
            fixable.append(f)
        else:
            print(f'  \u2713 {rel}')

    print(f'\n总计: {len(files)} 个文件, {len(fixable)} 个有问题, {issues_total} 项差异')

    if fixable:
        if yes_to_all:
            for f in fixable:
                rel = _rel_path(f)
                if 'archetypes' in rel:
                    print(f'  跳过模板: {rel}')
                    continue
                f.write_text(rebuild_from_base(f), encoding='utf-8')
                print(f'  已更新: {rel}')
        elif interactive:
            for f in fixable:
                rel = _rel_path(f)
                if 'archetypes' in rel:
                    print(f'  跳过模板: {rel}')
                    continue
                print(f'\n\u2500\u2500 {rel} \u2500\u2500')
                ans = input('是否按 archetype.html 重建？[Y/n]: ').strip().lower()
                if ans in ('y', ''):
                    f.write_text(rebuild_from_base(f), encoding='utf-8')
                    print(f'  已更新: {rel}')
                else:
                    print(f'  已跳过: {rel}')

    return len(fixable) == 0


def rebuild_all(yes=False):
    files = _find_html_files()
    print(f'全站模板同步: 扫描到 {len(files)} 个 HTML 文件\n')

    count = 0
    for f in files:
        rel = _rel_path(f)
        if 'archetypes' in rel:
            continue
        if not yes:
            ans = input(f'  {rel}  重建？[Y/n]: ').strip().lower()
            if ans not in ('', 'y'):
                print('    \u2713 跳过')
                continue
        f.write_text(rebuild_from_base(f), encoding='utf-8')
        print(f'  \u2713 {rel}')
        count += 1

    print(f'\n完成: 已同步 {count} 个文件')
