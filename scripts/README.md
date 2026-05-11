# scripts/ — 博客构建工具

## 文件结构

```
scripts/
├── build.py           # 入口：CLI 参数解析 + 交互菜单循环
├── config.py          # 常量：路径、分类定义、模板
├── utils.py           # 工具函数：slugify、ask、confirm、front matter 解析、干支日期转换
├── templint.py        # 模板一致性检查：对比所有 HTML 与 base.html
├── content.py         # 内容生成：Markdown 渲染、图片处理、文章发布
├── management.py      # 文章管理：列表、删除、文件管理器、标题/日期修改
├── requirements.txt   # Python 依赖（markdown、Pygments、lunar_python）
├── build.sh           # Shell 启动脚本（激活 venv 后运行 build.py）
├── venv/              # Python 虚拟环境（gitignored）
└── README.md          # 本文件
```

---

## 模块职责

### `build.py` — 入口

```sh
python build.py                           # 交互菜单
python build.py -f article.md -c sylvae   # CLI 模式
python build.py --list                    # 文章列表
python build.py --delete                  # 删除文章
python build.py --rename                  # 管理目录
python build.py --retitle                 # 修改标题
python build.py --check-template          # 检查模板
python build.py --git                     # Git 提交与推送
python build.py --lunar-date              # 获取当前干支日期
```

**交互菜单**：
```
  0. 退出工具
  1. 文章列表
  2. 发布文章
  3. 删除文章
  4. 修改标题
  5. 管理目录
  6. 检查模板
  7. 获取日期
  8. Git

请选择功能 [0]:
```

**所有交互功能支持 `q` 中途退出**

**逻辑**：
1. 解析 argparse 参数
2. `--list` / `--delete` / `--rename` / `--retitle` / `--git` → 直接调用对应函数后返回
3. `-f` → CLI 发布模式，调用 `content.publish_article()` 后返回
4. 无参数 → 交互菜单循环，用户选择功能后分发

---

### `config.py` — 常量

| 变量 | 说明 |
|------|------|
| `SCRIPT_DIR` | `scripts/` 目录绝对路径 |
| `ROOT_DIR` | 项目根目录 |
| `TEMPLATE_PATH` | `archetypes/article.html` |
| `CATEGORIES` | 分类列表 `[(key, name), ...]`，决定新增/删除时的选项 |
| `SECTION_MAP` | 分类 key → 中文名 |
| `PAGE_MAP` | 分类 key → 对应汇总页路径 |
| `ENTRY_TEMPLATE` | 汇总页 `<li>` 条目模板，含 `%%CATEGORY%%` 等占位符 |

> 新增分类时需要在 `CATEGORIES`、`SECTION_MAP`、`PAGE_MAP` 三处注册。

---

### `templint.py` — 模板一致性检查

| 函数 | 说明 |
|------|------|
| `check_all(interactive=True)` | 扫描所有 `.html` 文件，对照 `archetypes/base.html` 检查结构是否一致；`interactive=True` 时逐个询问是否重建 |
| `check_file(file_path, ...)` | 对单个文件检查 doctype、head 元数据、header/导航/页脚结构，返回问题列表 |
| `rebuild_from_base(file_path)` | 以 `base.html` 为骨架重建文件，保留 `<main>` 内容和 KaTeX 等额外 head 元素，自动适配相对路径深度 |

---

### `utils.py` — 工具函数

| 函数 | 说明 |
|------|------|
| `slugify(text)` | 生成 PascalCase slug（`Hello World` → `Hello-World`，全大写缩写保留） |
| `ask(prompt, default)` | 带默认值的输入提示 |
| `confirm(prompt, default='y')` | 统一 `[y/n]` 确认提示，默认 y，y/Y/n/N 均识别 |
| `parse_front_matter(text)` | 解析 Markdown front matter（`---` 分隔的 key:value），返回 `(meta_dict, body)` |
| `get_lunar_date(target_date=None)` | 将日期转换为干支格式。留空返回当前日期；`target_date` 传入 `datetime` 对象可指定日期 |

---

### `content.py` — 内容生成

**发布流程**（`publish_article(md_path, args, is_cli_mode)`）：

```
Markdown → parse_front_matter → 交互选择分类/标题/文件夹 → render_markdown → process_images → fill_template → 写入
```

| 函数 | 说明 |
|------|------|
| `process_obsidian_links(text)` | 将 Obsidian wiki 图片 `![[file.jpg]]` 转为标准 Markdown |
| `render_markdown(text)` | MD → HTML，启用 `extra`、`codehilite` 和 `nl2br` 扩展 |
| `process_images(html, md_path, output_dir)` | 查找 `<img>` 中的本地图片路径，复制到输出文件夹，更新 `src` 为相对路径 |
| `fill_template(template, title, date, content, section)` | 替换模板中的 `{{ title }}`、`{{ date }}`、`{{ content }}`、`{{ section }}` |
| `select_category_interactive()` | 交互式选择分类编号 |
| `publish_article(...)` | 主发布流程（见上方），返回 `True`（成功）或 `False`（取消） |

**交互发布流程**：
1. 输入 Markdown 文件路径（支持 `q` 退出）
2. 输入/确认日期（默认当前干支日期，如 `8 May. 2026 / 丙午年 癸巳月 壬午日`；留空即采用默认值）
3. 选择分类
4. 输入/确认标题（默认从文件名或 front matter）
5. 输入/确认文件夹名（默认从标题 slugify）
6. 确认发布

**注意**：
- 图片查找顺序：Markdown 文件同目录 → 项目根目录
- 远程图片（http/https/data:）跳过处理
- Markdown 中单个换行符自动转为 `<br />`，双换行符转为段落分隔

---

### `management.py` — 文章管理

| 函数 | 说明 |
|------|------|
| `list_articles(show_all=True)` | 先选分类（可选 0 列出全部），再显示该分类下的文章。支持 `q` 退出。返回 `{cat: {name, articles}}` |
| `delete_article()` | 先选分类 → 选文章 → 确认 → 删除文件夹 + 从分类页移除条目。支持 `q` 退出。 |
| `retitle_article()` | 先选分类 → 选文章 → 修改标题/日期 → 更新文章 HTML + 分类页条目。支持 `q` 退出。 |
| `file_manager()` | 文件浏览器：导航树 + 文件/目录操作 |
| `_file_ops(path)` | 对选定文件/目录的操作菜单：e(进入目录)/r(重命名)/d(删除)/m(标记移动) |
| `_update_refs(old_path, new_path)` | 全局搜索引用旧路径的文件并替换为新路径 |
| `_remove_entry_from_page(cat_key, folder)` | 从分类页中移除指定文章的 `<li>` 条目 |
| `add_entry_to_page(page_path, title, date, category, folder)` | 在分类页中添加或更新文章条目（去重） |
| `show_directory_tree()` | 打印 `content/` 下的文章文件夹树 |

**引用更新范围**（`_update_refs` 搜索的文件）：

```
pages/*.html, content/**/*.html, archetypes/*.html
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
