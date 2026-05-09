import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR, CATEGORIES, PAGE_MAP, ENTRY_TEMPLATE


def list_articles():
    print('=== 文章列表 ===\n')
    all_articles = {}

    for cat_key, cat_name in CATEGORIES:
        cat_dir = ROOT_DIR / 'content' / cat_key
        if not cat_dir.exists():
            continue

        articles = []
        for folder in sorted(cat_dir.iterdir()):
            if folder.is_dir() and (folder / 'index.html').exists():
                html = (folder / 'index.html').read_text(encoding='utf-8')
                title_match = re.search(r'<h2>([^<]+)</h2>', html)
                title = title_match.group(1) if title_match else folder.name
                articles.append({'title': title, 'folder': folder.name})

        if articles:
            all_articles[cat_key] = {'name': cat_name, 'articles': articles}

    for cat_key, data in all_articles.items():
        print(f'【{data["name"]}】')
        for i, art in enumerate(data['articles'], 1):
            print(f'  {i}. {art["title"]}')
            print(f'     文件夹: {art["folder"]}')
        print()

    if not all_articles:
        print('暂无文章\n')

    return all_articles


def select_category_index(prompt='分类编号 [1]: '):
    while True:
        try:
            idx = int(input(prompt).strip() or '1') - 1
            if 0 <= idx < len(CATEGORIES):
                return idx
        except ValueError:
            pass
        print('  无效选择，请重试')


def delete_article():
    all_articles = list_articles()

    if not all_articles:
        print('没有可删除的文章。')
        return

    print('分类:')
    for i, (key, name) in enumerate(CATEGORIES, 1):
        print(f'  {i}. {name} ({key})')

    while True:
        idx = select_category_index()
        cat_key = CATEGORIES[idx][0]
        if cat_key in all_articles:
            break
        print('  该分类暂无文章，请重试')

    articles = all_articles[cat_key]['articles']

    while True:
        try:
            idx = int(input(f'选择要删除的文章编号 (1-{len(articles)}): ').strip()) - 1
            if 0 <= idx < len(articles):
                break
        except ValueError:
            pass
        print('  无效编号，请重试')

    article = articles[idx]
    folder = article['folder']
    title = article['title']

    print(f'\n确认删除:')
    print(f'  标题: {title}')
    print(f'  文件夹: content/{cat_key}/{folder}/')
    confirm = input('确定要删除? [y/n]: ').strip().lower()
    if confirm not in ['y', '']:
        print('  已取消')
        return

    article_dir = ROOT_DIR / 'content' / cat_key / folder
    if article_dir.exists():
        shutil.rmtree(article_dir)
        print(f'  已删除文件夹: content/{cat_key}/{folder}/')

    page_path = PAGE_MAP.get(cat_key)
    if page_path and page_path.exists():
        lines = page_path.read_text(encoding='utf-8').splitlines(keepends=True)
        href_line = None
        for i, line in enumerate(lines):
            if f'href="../content/{cat_key}/{folder}/index.html"' in line:
                href_line = i
                break

        if href_line is not None:
            start = href_line
            while start >= 0 and '<li>' not in lines[start]:
                start -= 1
            end = href_line
            while end < len(lines) and '</li>' not in lines[end]:
                end += 1
            if end < len(lines):
                end += 1
            del lines[start:end]
            new_content = ''.join(lines)
            new_content = re.sub(r'\n\s*\n\s*<ul>', '\n<ul>', new_content)
            page_path.write_text(new_content, encoding='utf-8')
            print(f'  已从页面移除: pages/{cat_key}.html')
        else:
            print(f'  未在页面中找到对应条目: pages/{cat_key}.html')

    print('\n  删除完成!')


def add_entry_to_page(page_path, title, date, category, folder):
    if not page_path.exists():
        return False

    entry = (ENTRY_TEMPLATE
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


def show_directory_tree():
    content_dir = ROOT_DIR / 'content'
    if not content_dir.exists():
        print('  content/ (空)')
        return

    print('  content/')
    for cat_key, cat_name in CATEGORIES:
        cat_dir = content_dir / cat_key
        print(f'    ├── {cat_key}/')
        if cat_dir.exists():
            folders = sorted([d for d in cat_dir.iterdir() if d.is_dir() and (d / 'index.html').exists()])
            for i, folder in enumerate(folders):
                prefix = '    │   └── ' if i == len(folders) - 1 else '    │   ├── '
                print(f'{prefix}{folder.name}/')
    print()


def _get_project_path(path):
    return path.relative_to(ROOT_DIR).as_posix()


def _update_refs(old_path, new_path):
    old_str = _get_project_path(old_path)
    new_str = _get_project_path(new_path)

    glob_patterns = [
        (ROOT_DIR / 'pages', '*.html'),
        (ROOT_DIR / 'content', '**/*.html'),
        (ROOT_DIR / 'template', '*.html'),
        (ROOT_DIR / 'assets', '**/*.html'),
    ]
    single_files = [
        ROOT_DIR / 'index.html',
        ROOT_DIR / 'style.css',
        ROOT_DIR / 'README.md',
        ROOT_DIR / 'AGENTS.md',
    ]

    search_files = []
    for base, pattern in glob_patterns:
        if base.exists():
            search_files.extend(base.glob(pattern))
    for f in single_files:
        if f.exists():
            search_files.append(f)

    updated = []
    for f in search_files:
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        if old_str in text:
            new_text = text.replace(old_str, new_str)
            f.write_text(new_text, encoding='utf-8')
            updated.append(_get_project_path(f))

    return updated


def _remove_entry_from_page(cat_key, folder):
    page_path = PAGE_MAP.get(cat_key)
    if not page_path or not page_path.exists():
        return
    lines = page_path.read_text(encoding='utf-8').splitlines(keepends=True)
    idx = None
    for i, line in enumerate(lines):
        if f'href="../content/{cat_key}/{folder}/index.html"' in line:
            idx = i
            break
    if idx is None:
        return
    start = idx
    while start >= 0 and '<li>' not in lines[start]:
        start -= 1
    end = idx
    while end < len(lines) and '</li>' not in lines[end]:
        end += 1
    if end < len(lines):
        end += 1
    del lines[start:end]
    new_content = ''.join(lines)
    new_content = re.sub(r'\n\s*\n\s*<ul>', '\n<ul>', new_content)
    page_path.write_text(new_content, encoding='utf-8')


clipboard = {}


def file_manager():
    root = ROOT_DIR
    current = ROOT_DIR

    dirs_to_show = ['content', 'assets']

    dir_mode = True
    current_top_level = 0

    while True:
        entries = sorted(current.iterdir())
        dirs = sorted([e for e in entries if e.is_dir() and e.name not in ['scripts', '.git']])
        files = sorted([e for e in entries if e.is_file() and e.suffix in ['.html', '.css', '.md', '.otf', '.ttf', '.woff2', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']])

        items = dirs + files

        print(f'\n> {_get_project_path(current) if current != root else "."}')
        print('─' * 40)

        if current != root:
            print('  [0] .. (上级目录)')

        for i, item in enumerate(items, 1):
            if item.is_dir():
                print(f'  [{i}] 📁 {item.name}/')
            else:
                size = item.stat().st_size
                print(f'  [{i}] 📄 {item.name} ({size:,} B)')

        print()

        if clipboard.get('source'):
            print(f'  [v] 粘贴到此处 ({_get_project_path(clipboard["source"])})\n')

        raw = input('输入编号选择，q 退出: ').strip().lower()

        if raw == 'q':
            break

        if raw == '0' and current != root:
            current = current.parent
            continue

        if raw == 'v' and clipboard.get('source'):
            src = clipboard['source']
            if src.parent.resolve() == current.resolve():
                print('  源与目标相同，已取消')
                clipboard.clear()
                continue
            new_path = current / src.name
            if new_path.exists():
                print('  目标已存在，已取消')
                clipboard.clear()
                continue
            src.rename(new_path)
            updated = _update_refs(src, new_path)
            print(f'  已移动到: {_get_project_path(new_path)}')
            if updated:
                for u in updated:
                    print(f'    更新引用: {u}')
            if src.parent.parent.name == 'content' and src.parent.name in [c[0] for c in CATEGORIES]:
                _remove_entry_from_page(src.parent.name, src.name)
            clipboard.clear()
            continue

        try:
            idx = int(raw) - 1
            if 0 <= idx < len(items):
                selected = items[idx]
                result = _file_ops(selected)
                if result and selected.is_dir():
                    current = result
                continue
        except ValueError:
            pass

        msg = f'  无效选择: {raw}'
        print(msg)


def _file_ops(path):
    rel = _get_project_path(path)
    is_dir = path.is_dir()

    while True:
        kind = '文件夹' if is_dir else '文件'
        print(f'\n> {rel} ({kind})')
        print('─' * 32)
        if is_dir:
            print('  [e] 进入')
        print('  [r] 重命名')
        print('  [d] 删除')
        print('  [m] 标记/移动')
        print('  [b] 返回')
        print()

        op = input('选择操作: ').strip().lower()

        if op == 'b':
            break

        if op == 'e' and is_dir:
            return path

        elif op == 'r':
            default = path.name
            new_name = input(f'新名称 [{default}]: ').strip() or default
            if new_name == path.name:
                print('  名称相同，已取消')
                continue

            new_path = path.parent / new_name
            if new_path.exists():
                print('  目标已存在，已取消')
                continue

            path.rename(new_path)
            updated = _update_refs(path, new_path)
            print(f'  已重命名为 {new_name}')
            if updated:
                for u in updated:
                    print(f'    更新引用: {u}')

            if is_dir:
                parent_cat = path.parent.name
                parent_parent = path.parent.parent.name
                if parent_parent == 'content' and parent_cat in [c[0] for c in CATEGORIES]:
                    _remove_entry_from_page(parent_cat, path.name)

            break

        elif op == 'd':
            confirm = input(f'删除 {rel}? [y/n]: ').strip().lower()
            if confirm not in ['y', '']:
                continue

            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f'  已删除: {rel}')

            if is_dir:
                parent_cat = path.parent.name
                parent_parent = path.parent.parent.name
                if parent_parent == 'content' and parent_cat in [c[0] for c in CATEGORIES]:
                    _remove_entry_from_page(parent_cat, path.name)

            break

        elif op == 'm':
            print(f'  已标记: {rel}')
            print('  请导航到目标目录后输入 v 执行移动')
            clipboard['source'] = path
            break

        else:
            print('  无效操作')


def retitle_article():
    all_articles = list_articles()
    if not all_articles:
        print('没有可修改的文章。')
        return

    print('分类:')
    for i, (key, name) in enumerate(CATEGORIES, 1):
        print(f'  {i}. {name} ({key})')

    while True:
        idx = select_category_index()
        cat_key = CATEGORIES[idx][0]
        if cat_key in all_articles:
            break
        print('  该分类暂无文章，请重试')

    articles = all_articles[cat_key]['articles']

    while True:
        try:
            idx = int(input(f'选择文章编号 (1-{len(articles)}): ').strip()) - 1
            if 0 <= idx < len(articles):
                break
        except ValueError:
            pass
        print('  无效编号，请重试')

    article = articles[idx]
    folder = article['folder']

    html_path = ROOT_DIR / 'content' / cat_key / folder / 'index.html'
    html = html_path.read_text(encoding='utf-8')

    old_title = re.search(r'<h2>([^<]+)</h2>', html).group(1)
    old_date_match = re.search(r'<p class="post-date">(.*?)</p>', html)
    old_date = old_date_match.group(1).strip() if old_date_match else ''

    print(f'\n当前文章:')
    print(f'  标题: {old_title}')
    print(f'  日期: {old_date}')
    print(f'  文件夹: content/{cat_key}/{folder}/\n')

    new_title = input(f'新标题 [{old_title}]: ').strip() or old_title
    new_date = input(f'新日期 [{old_date}]: ').strip() or old_date

    if new_title == old_title and new_date == old_date:
        print('  无变化，已取消')
        return

    print(f'\n将修改:')
    print(f'  标题: {old_title} → {new_title}')
    print(f'  日期: {old_date} → {new_date}')
    confirm = input('确认修改? [y/n]: ').strip().lower()
    if confirm not in ['y', '']:
        print('  已取消')
        return

    html = html.replace(f'<title>{old_title}', f'<title>{new_title}', 1)
    html = html.replace(f'<h2>{old_title}</h2>', f'<h2>{new_title}</h2>', 1)
    html = html.replace(f'<p class="post-date">{old_date}</p>', f'<p class="post-date">{new_date}</p>', 1)
    html_path.write_text(html, encoding='utf-8')
    print(f'  - 已更新: content/{cat_key}/{folder}/index.html')

    page_path = PAGE_MAP.get(cat_key)
    if page_path and page_path.exists():
        new_entry = (ENTRY_TEMPLATE
                     .replace('%%CATEGORY%%', cat_key)
                     .replace('%%FOLDER%%', folder)
                     .replace('%%TITLE%%', new_title)
                     .replace('%%DATE%%', new_date))

        content = page_path.read_text(encoding='utf-8')
        pattern = re.compile(
            r'<li>\s*<a\s+href="../content/' + re.escape(cat_key) + r'/' + re.escape(folder) + r'/index.html"[^>]*>.*?</li>',
            re.DOTALL
        )
        match = pattern.search(content)
        if match:
            content = content[:match.start()] + new_entry.strip() + content[match.end():]
            page_path.write_text(content, encoding='utf-8')
            print(f'  - 已更新: pages/{cat_key}.html')
        else:
            print(f'  - 未找到条目: pages/{cat_key}.html')

    print('\n  修改完成!')
