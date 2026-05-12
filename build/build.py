#!/usr/bin/env python3
"""将 Markdown 文章发布为 HTML，支持交互菜单和 CLI 两种模式。

用法:
  python build.py                           # 交互菜单
  python build.py -f article.md -c sylvae   # CLI 模式
  python build.py --list                    # 列出文章
  python build.py --delete                  # 删除文章
  python build.py --rename                  # 管理目录
  python build.py --retitle                 # 修改标题/日期
  python build.py --check-archetypes        # 模板检查
  python build.py --rebuild                 # 全站模板同步
  python build.py --build-all               # 一键全量构建（模板同步+检查）
  python build.py --git                     # Git 提交+推送
  python build.py --lunar-date              # 干支日期
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR, CATEGORIES
from management import (
    list_articles, list_articles_direct,
    delete_article, delete_article_direct,
    file_manager,
    retitle_article, retitle_article_direct,
)
from content import publish_article
from templint import check_all, rebuild_all
from git_ops import git_commit_push
from utils import get_lunar_date


def parse_args():
    cat_choices = [c[0] for c in CATEGORIES]
    cat_help = '分类 (' + '/'.join(cat_choices) + ')'

    parser = argparse.ArgumentParser(
        description='将 Markdown 文章发布为 HTML，并自动更新分类汇总页',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python build.py                           # 交互菜单
  python build.py -f article.md -c sylvae   # CLI 完整流程
  python build.py -f article.md -c sylvae -y# CLI 跳过确认
  python build.py -f article.md -c sylvae -t "标题" -d "2025-01-01"

文章管理（交互式）:
  python build.py --list                    # 列出所有文章
  python build.py --delete                  # 删除文章
  python build.py --rename                  # 管理目录
  python build.py --retitle                 # 修改标题/日期

文章管理（非交互式 CLI）:
  python build.py --list-cat sylvae         # 直接列出指定分类文章
  python build.py --delete-by sylvae Slug-Name -y  # 直接删除
  python build.py --retitle-by sylvae Slug-Name -t "New Title" -d "Date"  # 直接修改

模板与全站:
  python build.py --check-archetypes        # 检查模板一致性
  python build.py --rebuild                 # 同步全站模板
  python build.py --build-all               # 一键全量构建（模板同步+检查）

其他:
  python build.py --git                     # Git
  python build.py --lunar-date              # 获取当前干支日期
        '''
    )
    # 文章发布参数
    parser.add_argument('-f', '--file', type=str,
                        help='Markdown 文件路径')
    parser.add_argument('-c', '--category', type=str,
                        choices=cat_choices,
                        help=cat_help)
    parser.add_argument('-t', '--title', type=str,
                        help='文章标题')
    parser.add_argument('-d', '--date', type=str,
                        help='发布日期')
    parser.add_argument('--folder', type=str,
                        help='文章文件夹名')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='跳过确认步骤')

    # 文章管理 —— 交互式
    parser.add_argument('--list', action='store_true',
                        help='列出文章（交互式选择分类）')
    parser.add_argument('--delete', action='store_true',
                        help='删除文章（交互式选择）')
    parser.add_argument('--rename', action='store_true',
                        help='管理目录（交互式文件管理器）')
    parser.add_argument('--retitle', action='store_true',
                        help='修改标题/日期（交互式选择）')

    # 文章管理 —— 非交互式
    parser.add_argument('--list-cat', type=str,
                        help='直接列出指定分类的文章')
    parser.add_argument('--delete-by', nargs=2,
                        metavar=('CATEGORY', 'SLUG'),
                        help='直接删除文章（指定分类和文件夹名）')
    parser.add_argument('--retitle-by', nargs=2,
                        metavar=('CATEGORY', 'SLUG'),
                        help='直接修改文章标题/日期（需配合 -t/-d）')

    # 模板与全站
    parser.add_argument('--check-archetypes', action='store_true',
                        help='检查模板一致性')
    parser.add_argument('--rebuild', action='store_true',
                        help='全站模板同步')
    parser.add_argument('--build-all', action='store_true',
                        help='一键全量构建（模板同步+检查）')

    # 其他
    parser.add_argument('--git', action='store_true',
                        help='Git 提交并推送')
    parser.add_argument('--lunar-date', action='store_true',
                        help='获取当前干支日期')

    return parser.parse_args()


def resolve_path(path_str):
    path = Path(path_str)
    return path if path.is_absolute() else ROOT_DIR / path


def main():
    args = parse_args()

    # ── 非交互式 CLI 命令 ──

    if args.list_cat:
        list_articles_direct(args.list_cat)
        return

    if args.list:
        list_articles()
        return

    if args.delete_by:
        cat, slug = args.delete_by
        delete_article_direct(cat, slug, yes=args.yes)
        return

    if args.delete:
        delete_article()
        return

    if args.rename:
        file_manager()
        return

    if args.retitle_by:
        cat, slug = args.retitle_by
        retitle_article_direct(cat, slug, args.title, args.date)
        return

    if args.retitle:
        retitle_article()
        return

    if args.check_archetypes:
        check_all(interactive=True, yes_to_all=args.yes)
        return

    if args.rebuild:
        rebuild_all(yes=args.yes)
        return

    if args.build_all:
        print('=== 一键全量构建 ===\n')
        print('[1/2] 同步全站模板...')
        rebuild_all(yes=True)
        print()
        print('[2/2] 检查模板一致性...')
        check_all(interactive=False, yes_to_all=True)
        print('\n全量构建完成!')
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

    # ── 交互式菜单模式 ──

    MENU_OPTIONS = {
        '1':  ('文章列表',     list_articles),
        '2':  ('发布文章',     None),
        '3':  ('删除文章',     delete_article),
        '4':  ('修改标题',     retitle_article),
        '5':  ('管理目录',     file_manager),
        '6':  ('检查模板',     lambda: check_all(interactive=True)),
        '7':  ('获取日期',     None),
        '8':  ('重建页面',     None),
        '9':  ('Git',         git_commit_push),
    }

    while True:
        print('=== 博客管理工具 ===\n')
        print('  0. 退出工具')
        for key, (label, _) in MENU_OPTIONS.items():
            print(f'  {key}. {label}')
        print()

        valid = ['', '0', 'q'] + list(MENU_OPTIONS.keys())
        choice = input('请选择功能 [0]: ').strip().lower()
        if choice not in valid:
            print('  无效选择，请重试\n')
            continue

        if choice == 'q' or choice == '0' or choice == '':
            print('已退出')
            break

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
            print('=== 重建页面（根据模板重建所有页面）===\n')
            raw = input('模式: [1] 逐个询问  [2] 全部自动 (回车/q 取消): ').strip().lower()
            if raw in ('', 'q'):
                print('  已取消')
                input('\n按回车键继续...')
                continue
            interactive_mode = (raw == '1')
            if interactive_mode:
                print('[1/2] 逐个同步...')
                rebuild_all(yes=False)
                print()
                print('[2/2] 检查并逐个修复...')
                check_all(interactive=True)
            else:
                print('[1/2] 全部自动重建...')
                rebuild_all(yes=True)
                print()
                print('[2/2] 检查模板一致性...')
                check_all(interactive=False, yes_to_all=True)
            print('\n完成!')
            input('\n按回车键继续...')
            continue

        _, action = MENU_OPTIONS[choice]
        if action:
            action()
        input('\n按回车键继续...')


if __name__ == '__main__':
    main()
