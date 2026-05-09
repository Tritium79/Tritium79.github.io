#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 build.py
read -p "按回车键退出..."