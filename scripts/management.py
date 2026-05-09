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
