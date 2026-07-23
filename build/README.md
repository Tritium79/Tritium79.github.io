# build/ — 博客构建工具

## 文件结构

```
build/
├── build.py           # 入口：CLI 参数解析 + 交互菜单循环
├── build.sh           # Shell 启动脚本（激活 venv 后运行 build.py）
├── config.py          # 常量：路径、分类定义、汇总页条目模板
├── data_loader.py     # 数据加载：从 data/*.json 读取全站配置
├── content.py         # 内容生成：Markdown 渲染、图片处理、文章发布
├── management.py      # 文章管理：列表、删除、文件管理器、标题/日期修改
├── templint.py        # 模板一致性检查 + 全站 Shell 同步引擎
├── utils.py           # 工具函数：slugify、ask、confirm、front matter 解析、干支日期
├── git_ops.py         # Git 提交与推送
├── requirements.txt   # Python 依赖（markdown、Pygments、lunar_python）
├── venv/              # Python 虚拟环境（gitignored）
└── README.md          # 本文件
```

---

## 模块职责

### `build.py` — 入口

```sh
python build.py                           # 交互菜单
python build.py -f article.md -c sylvae   # CLI 发布模式
python build.py --list                    # 交互式文章列表
python build.py --list-cat sylvae         # 非交互式列表
python build.py --delete                  # 交互式删除
python build.py --delete-by sylvae slug   # 非交互式删除
python build.py --rename                  # 交互式文件管理器
python build.py --retitle                 # 交互式修改标题/日期
python build.py --retitle-by slug -t "新标题" -d "日期"  # 非交互式
python build.py --check-archetypes        # 模板一致性检查
python build.py --rebuild                 # 全站 Shell 同步
python build.py --build-all               # 一键全量构建（模板同步+检查）
python build.py --git                     # Git 提交与推送
python build.py --lunar-date              # 干支日期
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
  8. 重建页面（根据模板重建，可选逐个/全部模式）
  9. Git
```

**所有交互功能支持 `q` 中途退出**

**入口逻辑**：
1. 解析 argparse 参数
2. 命中非交互 CLI 参数 → 直接执行并返回
3. `-f` → CLI 发布模式 → `content.publish_article()`
4. 无参数 → 进入交互菜单循环

---

### `config.py` — 常量

| 变量 | 说明 |
|------|------|
| `SCRIPT_DIR` | `build/` 目录绝对路径 |
| `ROOT_DIR` | 项目根目录 |
| `ARCHETYPE_PATH` | `archetypes/archetype.html` |
| `CATEGORIES` | 分类列表 `[(key, name), ...]`，从 `data/categories.json` 加载 |
| `SECTION_MAP` | 分类 key → 中文简称，从 `data/categories.json` 加载 |
| `PAGE_MAP` | 分类 key → 对应汇总页路径，从 `data/categories.json` 加载 |
| `ENTRY_TEMPLATE` | 汇总页 `<li>` 条目模板，含 `%%CATEGORY%%` 等占位符 |

> `CATEGORIES` / `SECTION_MAP` / `PAGE_MAP` 由 `data/categories.json` 驱动，新增分类时编辑该文件即可。

---

### `data_loader.py` — 数据加载

从 `data/*.json` 读取全站配置，所有函数均提供 fallback 默认值，数据文件缺失时不会中断流程。

| 函数 | 来源 | 用途 |
|------|------|------|
| `get_site_title()` | `data/config.json` | 博客标题 |
| `get_site_url()` | `data/config.json` | 站点 URL |
| `get_html_lang()` | `data/config.json` | HTML 语言属性 |
| `get_avatar()` | `data/config.json` | 头像文件名 |
| `get_css_file()` | `data/config.json` | 样式表文件名 |
| `get_footer()` | `data/config.json` | 页脚 HTML |
| `get_nav()` | `data/config.json` | 导航列表 `[(href, cn, la), ...]` |
| `get_settings(key)` | `data/settings.json` | 构建过程设置（markdown、日期、文件管理器等） |
| `clear_cache()` | — | 清空文件缓存 |

**设计原则**：
- `data/config.json` — 站点身份配置（标题、语言、导航、页脚）
- `data/settings.json` — 构建过程配置（Markdown 扩展、日期格式、文件管理器行为等）
- 修改后运行 `--build-all` 即可同步全站

---

### `content.py` — 文章发布引擎

**发布流水线**：
```
Markdown → parse_front_matter → render_markdown（nl2br/codehilite）
  → process_images（本地图片复制） → fill_template → 写入 → add_entry_to_page
```

| 函数 | 说明 |
|------|------|
| `process_obsidian_links(text)` | `![[file.jpg]]` → `![file.jpg](file.jpg)` |
| `process_links(html)` | 为所有 `<a>` 加 `target="_blank"` |
| `render_markdown(text)` | MD → HTML（extra + codehilite + nl2br） |
| `process_images(html, md_path, output_dir)` | 查找本地图片并复制到输出目录 |
| `generate_nav_links(section, prefix)` | 从 `data/config.json` 生成导航 HTML |
| `fill_template(template, title, date, content, section)` | 填充 archetype.html 的所有模板变量（h2+date 拼入 content） |
| `publish_article(md_path, args, is_cli_mode)` | 主发布函数 |

**图片搜索顺序**：Markdown 同目录 → 项目根目录；远程图片（http/https/data:）跳过。

---



### `templint.py` — 模板检查与 Shell 同步

全站模板一致性检查和自动修复引擎。

| 函数 | 说明 |
|------|------|
| `check_file(file_path)` | 对照 `data/config.json` 检查单个文件结构完整性 |
| `check_all(interactive, yes_to_all)` | 扫描全站 HTML 并检查/修复 |
| `rebuild_from_base(file_path)` | 用当前 archetype.html 模板重建文件，保留 `<main>` 内容 |
| `rebuild_all(yes)` | 强制全站 Shell 同步（跳过 archetypes/ 模板） |

**检查依据**：`data/config.json` 的 `nav`（导航）和 `footer`（页脚），而非某个 HTML 参考文件。

**保护机制**：archetypes/ 下的文件不会被写入覆盖，`{{ nav_links }}` 和 `{{ footer_content }}` 的模板变量跳过检查。

---

### `management.py` — 文章管理

| 函数 | 交互 | 说明 |
|------|------|------|
| `list_articles(show_all)` | ✔️ | 选分类 → 列出文章 |
| `list_articles_direct(category)` | ❌ | 直接列出指定分类 |
| `delete_article()` | ✔️ | 选分类 → 选文章 → 确认删除 |
| `delete_article_direct(cat, slug, yes)` | ❌ | 直接按 slug 删除 |
| `retitle_article()` | ✔️ | 选分类 → 选文章 → 改标题/日期 |
| `retitle_article_direct(cat, slug, title, date)` | ❌ | 直接按 slug 修改 |
| `file_manager()` | ✔️ | 文件浏览器：导航、重命名、删除、标记移动 |
| `add_entry_to_page(path, title, date, cat, folder)` | ❌ | 在汇总页添加/更新条目（去重） |

**引用更新范围**（文件管理器重命名/移动时自动更新）：
```
pages/*.html, content/**/*.html, archetypes/*.html
assets/**/*.html, index.html, style.css, README.md, AGENTS.md
```

---

### `utils.py` — 工具函数

| 函数 | 说明 |
|------|------|
| `slugify(text)` | 生成 PascalCase slug，全大写缩写保留 |
| `ask(prompt, default)` | 带默认值的输入 |
| `confirm(prompt, default)` | `[y/n]` 确认 |
| `parse_front_matter(text)` | 解析 YAML front matter，返回 `(meta, body)` |
| `get_lunar_date(target_date)` | 干支日期，如 `8 May. 2026 / 丙午年 癸巳月 壬午日` |

---

### `git_ops.py` — Git 操作

| 函数 | 说明 |
|------|------|
| `git_commit_push()` | 交互式：git add . → 输入 commit message → 确认 push |

---

## 使用方式

### 终端
```sh
cd build
source venv/bin/activate
./build.sh --list       # 或直接 python3 build.py --list
```

### macOS 双击
双击 `Blog.command` 即可打开终端进入交互菜单。

### 依赖安装
```sh
cd build
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
