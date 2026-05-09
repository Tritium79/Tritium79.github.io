#!/usr/bin/env python3
"""将 Markdown 文章发布为 HTML，支持交互菜单和 CLI 两种模式。

用法:
  python build.py                           # 交互菜单
  python build.py -f article.md -c silvae   # CLI 模式
  python build.py --list                    # 列出文章
  python build.py --delete                  # 删除文章
  python build.py --rename                  # 管理目录
  python build.py --retitle                 # 修改标题/日期
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR, CATEGORIES
from management import list_articles, delete_article, file_manager, retitle_article
from content import publish_article
from templint import check_all
from git_ops import git_commit_push
from utils import get_lunar_date


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
  python build.py --rename                  # 管理目录
  python build.py --retitle                 # 修改标题/日期
  python build.py --check-template          # 模板检查
  python build.py --git                     # Git
  python build.py --lunar-date              # 获取当前干支日期
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
    parser.add_argument('--rename', action='store_true', help='管理目录')
    parser.add_argument('--retitle', action='store_true', help='修改标题/日期')
    parser.add_argument('--check-template', action='store_true', help='模板检查')
    parser.add_argument('--git', action='store_true', help='Git')
    parser.add_argument('--lunar-date', action='store_true', help='获取当前干支日期')

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

    if args.rename:
        file_manager()
        return

    if args.retitle:
        retitle_article()
        return

    if args.check_template:
        check_all(interactive=True, yes_to_all=args.yes)
        return

    if args.git:
        git_commit_push()
        return

    if args.lunar_date:
        print(get_lunar_date())
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
        print('  0. 退出工具')
        print('  1. 文章列表')
        print('  2. 发布文章')
        print('  3. 删除文章')
        print('  4. 修改标题')
        print('  5. 管理目录')
        print('  6. 检查模板')
        print('  7. 获取日期')
        print('  8. Git\n')

        choice = input('请选择功能 [0]: ').strip().lower()
        if choice not in ['', '0', '1', '2', '3', '4', '5', '6', '7', '8', 'q']:
            print('  无效选择，请重试\n')
            continue

        if choice == 'q' or choice == '0' or choice == '':
            print('已退出')
            break

        if choice == '1':
            list_articles()
            input('\n按回车键继续...')
            continue

        if choice == '2':
            print('=== Markdown 文章发布工具 ===\n')
            while True:
                raw = input('Markdown 文件路径 (q 退出): ').strip()
                if raw.lower() == 'q':
                    break
                md_path = resolve_path(raw) if raw else None
                if md_path and md_path.exists():
                    break
                print(f'  文件不存在: {raw if raw else "(空)"}')
            if raw.lower() == 'q':
                continue
            publish_article(md_path, args, is_cli_mode=False)
            input('\n按回车键继续...')
            continue

        if choice == '3':
            delete_article()
            input('\n按回车键继续...')
            continue

        if choice == '4':
            retitle_article()
            input('\n按回车键继续...')
            continue

        if choice == '5':
            file_manager()
            input('\n按回车键继续...')
            continue

        if choice == '6':
            check_all(interactive=True)
            input('\n按回车键继续...')
            continue

        if choice == '7':
            raw = input('输入日期 (20xx-xx-xx，留空为当前日期): ').strip()
            if raw:
                try:
                    target = datetime.strptime(raw, '%Y-%m-%d')
                    print(get_lunar_date(target))
                except ValueError:
                    print('  格式错误，请使用 20xx-xx-xx')
            else:
                print(get_lunar_date())
            input('\n按回车键继续...')
            continue

        if choice == '8':
            git_commit_push()
            input('\n按回车键继续...')
            continue


if __name__ == '__main__':
    main()
