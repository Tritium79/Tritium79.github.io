#!/usr/bin/env python3
"""将 Markdown 文章发布为 HTML，支持交互菜单和 CLI 两种模式。

用法:
  python build.py                           # 交互菜单
  python build.py -f article.md -c silvae   # CLI 模式
  python build.py --list                    # 列出文章
  python build.py --delete                  # 删除文章
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR, CATEGORIES
from management import list_articles, delete_article
from content import publish_article


def parse_args():
    parser = argparse.ArgumentParser(
        description='将 Markdown 文章发布为 HTML，并自动更新分类汇总页',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python build.py                           # 交互菜单
  python build.py -f article.md -c silvae   # CLI 完整流程
  python build.py -f article.md -c silvae -y# CLI 跳过确认
  python build.py -f article.md -c silvae -t "标题" -d "2025-01-01"

文章管理:
  python build.py --list                    # 列出所有文章
  python build.py --delete                  # 删除文章
        '''
    )
    parser.add_argument('-f', '--file', type=str, help='Markdown 文件路径')
    parser.add_argument('-c', '--category', type=str, choices=[c[0] for c in CATEGORIES],
                        help='分类 (silvae/commentarii/versiones/archivum)')
    parser.add_argument('-t', '--title', type=str, help='文章标题')
    parser.add_argument('-d', '--date', type=str, help='发布日期')
    parser.add_argument('--folder', type=str, help='文章文件夹名')
    parser.add_argument('-y', '--yes', action='store_true', help='跳过确认步骤')
    parser.add_argument('--list', action='store_true', help='列出所有文章')
    parser.add_argument('--delete', action='store_true', help='删除文章')

    return parser.parse_args()


def resolve_path(path_str):
    path = Path(path_str)
    return path if path.is_absolute() else ROOT_DIR / path


def main():
    args = parse_args()

    if args.list:
        list_articles()
        return

    if args.delete:
        delete_article()
        return

    if args.file:
        md_path = resolve_path(args.file)
        if not md_path.exists():
            print(f"错误: 文件不存在: {md_path}")
            sys.exit(1)
        publish_article(md_path, args, is_cli_mode=True)
        return

    while True:
        print('=== 博客管理工具 ===\n')
        print('  1. 发布新文章')
        print('  2. 列出所有文章')
        print('  3. 删除文章')
        print('  4. 退出\n')

        choice = input('请选择功能 [1]: ').strip()
        if choice not in ['', '1', '2', '3', '4']:
            print('  无效选择，请重试\n')
            continue

        if choice == '2':
            list_articles()
            input('\n按回车键继续...')
            continue

        if choice == '3':
            delete_article()
            input('\n按回车键继续...')
            continue

        if choice == '4':
            print('已退出')
            return

        while True:
            print('=== Markdown 文章发布工具 ===\n')
            while True:
                raw = input('Markdown 文件路径: ').strip()
                md_path = resolve_path(raw) if raw else None
                if md_path and md_path.exists():
                    break
                print(f'  文件不存在: {raw if raw else "(空)"}')

            publish_article(md_path, args, is_cli_mode=False)

            if input('\n按回车继续发布，输入 q 返回菜单: ').strip().lower() == 'q':
                break


if __name__ == '__main__':
    main()
