# scripts/ — 博客构建工具

## 文件结构

```
scripts/
├── build.py           # 入口：CLI 参数解析 + 交互菜单循环
├── config.py          # 常量：路径、分类定义、模板
├── utils.py           # 工具函数：slugify、ask、confirm、front matter 解析
├── content.py         # 内容生成：Markdown 渲染、图片处理、文章发布
├── management.py      # 文章管理：列表、删除、文件管理器、标题/日期修改
├── requirements.txt   # Python 依赖（markdown、Pygments）
├── build.sh           # Shell 启动脚本（激活 venv 后运行 build.py）
├── Blog.command       # macOS 双击启动脚本（运行后暂停）
├── venv/              # Python 虚拟环境（gitignored）
└── README.md          # 本文件
```

---

## 模块职责

### `build.py` — 入口

```sh
python build.py                           # 交互菜单
python build.py -f article.md -c silvae   # CLI 模式
python build.py --list                    # 列出文章
python build.py --delete                  # 删除文章
python build.py --rename                  # 文件管理器
python build.py --retitle                 # 修改标题/日期
```

**逻辑**：
1. 解析 argparse 参数
2. `--list` / `--delete` / `--rename` / `--retitle` → 直接调用 management.py 对应函数后返回
3. `-f` → CLI 发布模式，调用 `content.publish_article()` 后返回
4. 无参数 → 交互菜单循环，用户选择功能后分发

---

### `config.py` — 常量

| 变量 | 说明 |
|------|------|
| `SCRIPT_DIR` | `scripts/` 目录绝对路径 |
| `ROOT_DIR` | 项目根目录 |
| `TEMPLATE_PATH` | `template/article.html` |
| `CATEGORIES` | 分类列表 `[(key, name), ...]`，决定新增/删除时的选项 |
| `SECTION_MAP` | 分类 key → 中文名 |
| `PAGE_MAP` | 分类 key → 对应汇总页路径 |
| `ENTRY_TEMPLATE` | 汇总页 `<li>` 条目模板，含 `%%CATEGORY%%` 等占位符 |

> 新增分类时需要在 `CATEGORIES`、`SECTION_MAP`、`PAGE_MAP` 三处注册。

---

### `utils.py` — 工具函数

| 函数 | 说明 |
|------|------|
| `slugify(text)` | 生成 PascalCase slug（`Hello World` → `Hello-World`，全大写缩写保留） |
| `ask(prompt, default)` | 带默认值的输入提示 |
| `confirm(prompt, default='y')` | 统一 `[y/n]` 确认提示，默认 y，y/Y/n/N 均识别 |
| `parse_front_matter(text)` | 解析 Markdown front matter（`---` 分隔的 key:value），返回 `(meta_dict, body)` |

---

### `content.py` — 内容生成

**发布流程**（`publish_article(md_path, args, is_cli_mode)`）：

```
Markdown → parse_front_matter → render_markdown → process_images → fill_template → 写入
```

| 函数 | 说明 |
|------|------|
| `process_obsidian_links(text)` | 将 Obsidian wiki 图片 `![[file.jpg]]` 转为标准 Markdown |
| `render_markdown(text)` | MD → HTML，启用 `extra` 和 `codehilite` 扩展 |
| `process_images(html, md_path, output_dir)` | 查找 `<img>` 中的本地图片路径，复制到输出文件夹，更新 `src` 为相对路径 |
| `fill_template(template, title, date, content, section)` | 替换模板中的 `{{ title }}`、`{{ date }}`、`{{ content }}`、`{{ section }}` |
| `select_category_interactive()` | 交互式选择分类编号 |
| `publish_article(...)` | 主发布流程（见上方），返回 `True`（成功）或 `False`（取消） |

**注意**：
- 图片查找顺序：Markdown 文件同目录 → 项目根目录
- 远程图片（http/https/data:）跳过处理
- 模板中使用 `<!--sep-->` 标记手动换行位置（替换为 `<br />`）

---

### `management.py` — 文章管理

| 函数 | 说明 |
|------|------|
| `list_articles()` | 扫描 `content/` 下所有文章，打印分类、标题、文件夹名，返回 `{cat: {name, articles}}` |
| `delete_article()` | 交互选择 → 确认 → 删除文件夹 + 从分类页移除条目 |
| `retitle_article()` | 交互选择 → 修改标题/日期 → 更新文章 HTML + 分类页条目 |
| `file_manager()` | 文件浏览器：导航树 + 文件/目录操作 |
| `_file_ops(path)` | 对选定文件/目录的操作菜单：e(进入目录)/r(重命名)/d(删除)/m(标记移动) |
| `_update_refs(old_path, new_path)` | 全局搜索引用旧路径的文件并替换为新路径 |
| `_remove_entry_from_page(cat_key, folder)` | 从分类页中移除指定文章的 `<li>` 条目 |
| `add_entry_to_page(page_path, title, date, category, folder)` | 在分类页中添加或更新文章条目（去重） |
| `show_directory_tree()` | 打印 `content/` 下的文章文件夹树 |

**引用更新范围**（`_update_refs` 搜索的文件）：

```
pages/*.html, content/**/*.html, template/*.html
assets/**/*.html, index.html, style.css, README.md, AGENTS.md
```

**文件管理器操作流程**：

```
顶层（项目根）→ 选择目录 → [e]进入/[r]重命名/[d]删除/[m]标记
                                        ↓
                                   标记后导航到目标目录 → 输入 v 粘贴
```

---

## 使用方式

### macOS 双击
双击 `Blog.command` 即可打开终端进入交互菜单。

### 终端
```sh
cd scripts
source venv/bin/activate
./build.sh --list       # 或直接 python3 build.py --list
```

### 依赖安装
```sh
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
