"""Git 提交与推送的交互式封装。"""

import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOT_DIR
from data_loader import get_settings


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR)
    if result.returncode != 0:
        print(f'  git 错误: {result.stderr.strip()}')
        return False
    out = result.stdout.strip()
    if out:
        for line in out.split('\n'):
            print(f'  {line}')
    return True


def git_commit_push():
    print('=== Git ===\n')

    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=ROOT_DIR)
    if not status.stdout.strip():
        print('没有需要提交的更改。')
        return

    print('待提交的更改:')
    for line in status.stdout.strip().split('\n'):
        print(f'  {line}')
    print()

    confirm = input('执行 git add .？[Y/n]: ').strip().lower()
    if confirm not in ('', 'y'):
        print('  已取消')
        return

    print('\n  git add .')
    if not _run(['git', 'add', '.']):
        return

    fmt = get_settings('commit_message_format', '{date} Update')
    default_msg = fmt.format(date=date.today().isoformat())
    raw = input(f'提交信息 [{default_msg}]: ').strip()
    msg = raw if raw else default_msg

    print(f'\n  git commit -m "{msg}"')
    if not _run(['git', 'commit', '-m', msg]):
        return

    raw = input('\n是否推送？[y/N]: ').strip().lower()
    if raw not in ('', 'y'):
        print('  已跳过推送')
        return

    print('\n  git push')
    _run(['git', 'push'])

    print('\n  完成!')
