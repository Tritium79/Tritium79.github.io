# Tritium79's Blog

静态个人博客，使用 HTML + CSS。使用自制Python脚本管理。

> **注意：** 本 README-Full.md 应随目录结构变化而更新，反映最新结构。它是一份可变参考文档，而非静态档案。
>
> **快速上手 → 见 [README_Simplified.md](README_Simplified.md)**

---

## 目录结构

```
Tritium79.github.io/
├── index.html                  # 首页
├── style.css                   # CSS 入口（集中 @import）
│
├── assets/                     # 全局静态资源
│   ├── css/                    # 模块化 CSS 文件
│   ├── fonts/                  # 字体文件
│   │   └── lxgw/               # LXGW Bright 子集与分包产物（subset.css、result.css、woff2）
│   ├── icons/                  # 图标
│   └── images/                 # 图片资源
│
├── content/                    # 文章
│   ├── archivum/               # Archivum
│   │   └── {YYYYMMDD}_{Article-Slug}/
│   │       ├── index.html      # 生成的页面
│   │       ├── index.md        # 源 Markdown（图片路径已本地化）
│   │       └── (附属资源，如图片)
│   ├── commentarii/            # Commentarii
│   │   └── {YYYYMMDD}_{Article-Slug}/
│   │       ├── index.html
│   │       ├── index.md
│   │       └── (附属资源)
│   ├── sylvae/                 # Sylvae
│   │   └── {YYYYMMDD}_{Article-Slug}/
│   │       ├── index.html
│   │       ├── index.md
│   │       └── (附属资源)
│   └── transcripta/            # Transcripta
│       └── {YYYYMMDD}_{Article-Slug}/
│           ├── index.html
│           ├── index.md
│           └── (附属资源)
│
├── pages/                      # 章节
│   ├── archivum.html           # Archivum
│   ├── commentarii.html        # Commentarii
│   ├── deme.html               # De Me
│   ├── amici.html              # Amici
│   ├── sylvae.html             # Sylvae
│   └── transcripta.html        # Transcripta
│
├── build/                    # 构建脚本
│   ├── build.py                # 入口：CLI 参数解析 + 交互菜单
│   ├── build.sh                # Shell 封装（激活 venv 后运行 build.py）
│   ├── config.py               # 常量：路径、分类定义（从 data/ 加载）
│   ├── data_loader.py          # 数据加载：从 data/*.json 读取配置
│   ├── content.py              # 内容生成：Markdown 渲染、图片处理、文章发布
│   ├── font_subset.py          # 字体处理：扫描全站字符并生成字体子集
│   ├── management.py           # 文章管理：列表、删除、文件管理器、修改标题/日期
│   ├── utils.py                # 工具函数：slugify、ask、confirm、front matter 解析
│   ├── templint.py             # 模板一致性检查 + 全站 Shell 同步引擎
│   ├── git_ops.py              # Git 提交与推送
│   ├── requirements.txt        # Python 依赖
│   ├── README.md               # 脚本文档
│   └── venv/                   # Python 虚拟环境
│
├── archetypes/                   # HTML 模板
│   └── archetype.html           # 统一模板（{{ root_path }}/{{ nav_links }}/{{ footer_content }}，含 KaTeX）
│
├── data/                       # 全站数据配置（JSON）
│   ├── config.json             # 站点身份：标题、语言、导航、页脚、头像、CSS
│   ├── categories.json         # 章节定义：名称、路径、汇总页
│   └── settings.json           # 构建设置：Markdown 扩展、日期格式、文件管理器等
│
├── robots.txt                  # 爬虫规则：仅允许首页
├── README_Simplified.md        # 快速上手指南
├── .gitignore                  # Git 忽略规则
├── README-Full.md              # 目录结构与命名规范
├── README.md                   # 留空文档
└── AGENTS.md                   # AI 辅助审查指令
```

---

## 命名规则

### 章节（category）

| 章节 key            | 显示名称        |
|--------------------|----------------|
| `sylvae`           | Sylvae         |
| `commentarii`      | Commentarii    |
| `transcripta`      | Transcripta    |
| `archivum`         | Archivum       |

新增章节需同时在 `data/categories.json` 和 `data/config.json` 的 `nav` 中注册，并在 `pages/` 下创建对应的 `.html` 汇总页。

### 文章文件夹（slug）

- 每个文章一个独立文件夹，统一使用 `index.html` 作为入口文件
- 文件夹名使用 `{YYYYMMDD}_{Slug}` 格式，`YYYYMMDD` 为文章发布日期（自动生成），`Slug` 部分使用 slug 命名：单词首字母大写、其余字母小写、单词间以连字符 `-` 分隔
- 允许全大写缩写（如 `OA`、`HDR`、`LaTeX` 等专有名词保留原写法）
- 仅允许字母、数字、汉字、连字符
- 示例：`20260509_Blog-Init`、`20260508_Cat-Record`、`20260509_Code-LaTeX-HDR-Test`

### 附属资源

- 文章附属图片、文件等放置在同一文章文件夹内
- 引用路径使用相对路径（如 `Cat.jpg`）

### 汇总页

- `pages/{category}.html` — 按分类列出文章标题与日期
- 新增文章时，`build.py` 会自动在对应汇总页的 `<ul>` 中追加条目
- 仅当文章被真正删除时才手动移除对应条目

### 构建脚本

- `build/build.py` — 主构建脚本
- 工作流：Markdown 文件 → 解析 front matter → 渲染 HTML → 写入 `content/{category}/{slug}/index.html`（同时复制源 `.md` 并本地化图片路径） → 更新汇总页 → 扫描全站字符并按需更新字体子集
  - 交互菜单：

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
  9. 重建字体
  10. Git
```

- 所有功能支持 `q` 中途退出
- `python build.py --check-archetypes` — 对照 `data/config.json` 检查所有 HTML 文件的结构一致性（nav、footer 等），可选自动修复
- `python build.py --rebuild` — 全站 Shell 同步：用当前模板（archetype.html）+ 数据（data/config.json）重建所有页面，并同步字体子集
- `python build.py --build-all` — 一键全量：rebuild → subset-font → check-archetypes
- `python build.py --subset-font` — 强制根据全站 HTML 重新生成字体子集
- `python build.py --list-cat sylvae` — 非交互式列出指定分类文章
- `python build.py --delete-by sylvae YYYYMMDD_Slug-Name -y` — 非交互式删除文章
- `python build.py --retitle-by sylvae YYYYMMDD_Slug-Name -t "新标题" -d "新日期"` — 非交互式修改标题/日期
- `python build.py --git` — Git 提交与推送
- `python build.py --lunar-date` — 获取当前干支日期
- 发布文章时会自动检测全站字符集；字符有变化才重新生成 `assets/fonts/lxgw/subset-*.woff2`
- 所有路径以项目根目录为基准
- Markdown 渲染扩展由 `data/settings.json` 的 `markdown_extensions` 定义
- 发布文章时日期留空，默认使用当前干支日期（格式由 `data/settings.json` 的 `date_format` 定义）

### assets

- `fonts/` — 存放字体文件
- `fonts/lxgw/subset.css` — 全站字符子集的字体规则，优先于分包加载
- `fonts/lxgw/result.css` — cn-font-split 生成的分包规则，作为子集未覆盖字符的回退
- `icons/` — 存放图标文件
- `css/` — 模块化 CSS 文件（由 `style.css` 集中 `@import`）
- `images/` — 通用图片资源

---

## 全站数据驱动配置

站点层面的配置（导航、页脚等）通过 `data/` 目录下的 JSON 文件统一管理。这是全站的单点真相（Single Source of Truth）。

### data/config.json

```json
{
    "site": {
        "title": "Tritium79's Blog",
        "url": "https://Tritium79.github.io"
    },
    "html_lang": "zh-CN",
    "avatar": "avatar.png",
    "css_file": "style.css",
    "footer": "&copy; 2026 <a href=\"...\">Tritium79</a>. All rights reserved.",
    "nav": [
        {"href": "index.html", "la": "Domus"},
        {"href": "pages/sylvae.html", "la": "Sylvae"},
        {"href": "pages/commentarii.html", "la": "Commentarii"},
        {"href": "pages/transcripta.html", "la": "Transcripta"},
        {"href": "pages/archivum.html", "la": "Archivum"},
        {"href": "pages/amici.html", "la": "Amici"},
        {"href": "pages/deme.html", "la": "De Me"}
    ]
}
```

| 字段 | 用途 | 修改后 |
|------|------|--------|
| `site.title` | 全站标题，出现在 `<title>` 和 header | 运行 `--build-all` |
| `site.url` | 站点 URL，用于 footer 链接 | 运行 `--build-all` |
| `html_lang` | HTML 语言属性 (`lang`) | 运行 `--build-all` |
| `avatar` | 头像文件名 | 运行 `--build-all` |
| `css_file` | 样式表文件名 | 运行 `--build-all` |
| `footer` | 页脚 HTML 内容 | 运行 `--build-all` |
| `nav` | 导航链接数组，每项含 `href`/`la` | 运行 `--build-all` |

### data/settings.json

构建过程设置（Markdown 渲染、日期格式、文件管理器等），详见 `build/README.md`。



---

## 分类/章节扩展规范

新增分类需完成以下步骤：

1. **注册分类**：在 `data/categories.json` 中添加一条：
   ```json
   "your-key": {
        "name": "Latin",
        "page": "pages/your-key.html"
   }
   ```

2. **更新导航**：在 `data/config.json` 的 `nav` 数组中添加对应条目

3. **创建汇总页**：在 `pages/` 下创建 `{key}.html`，结构如下：
   ```html
   <main>
        <h2>Latin</h2>
       <p>描述...</p>
       <hr />
        <ol class="link-list">
            <!-- build.py 会自动在此处追加文章条目 -->
        </ol>
   </main>
   ```

4. **创建内容目录**：`content/{key}/`（build.py 发布时会自动创建）

5. **运行** `python build.py --build-all` 同步全站

---

## HTML 模板与结构规范

### 模板分工

| 模板 | 用途 | 路径变量 |
|------|------|---------|
| `archetypes/archetype.html` | 全站统一模板（手动页面 + 文章页） | `{{ root_path }}`（由构建脚本自动替换为 `/`、`../` 或 `../../../`） |

### 页面结构要求

所有页面必须包含以下结构：

```html
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>标题 | Tritium79's Blog</title>
    <link rel="stylesheet" href=".../style.css" />
</head>
<body>
    <header>...</header>
    <main>...</main>
    <footer>...</footer>
</body>
</html>
```

### 路径层级约定

| 页面位置 | CSS 路径 | 首页链接 | 头像/图片路径 |
|---------|---------|---------|-------------|
| 根目录 (`index.html`) | `style.css` | `index.html` | `assets/images/avatar.png` |
| `pages/*.html` | `../style.css` | `../index.html` | `../assets/images/avatar.png` |
| `content/*/*/index.html` | `../../../style.css` | `../../../index.html` | `../../../assets/images/avatar.png` |

### 导航格式

导航链接必须使用以下结构，不得更改：

```html
<a href="...">
    <span class="nav-la">Latin</span>
</a>
```

### 模板变量系统

`archetypes/archetype.html` 使用以下模板变量：

| 变量 | 用途 | 适用范围 | 示例值 |
|------|------|---------|--------|
| `{{ title }}` | 页面标题 `<title>` | base + article | `序` |
| `{{ section }}` | 当前章节名（nav-current / current-section） | base + article | `Sylvae` |
| `{{ section_href }}` | 当前章节导航页相对路径（current-section 链接目标） | base + article | `pages/sylvae.html` |
| `{{ body_class }}` | 非文章页的 body 类标记（` class="section-page"` 或空） | base + article | ` class="section-page"` |
| `{{ content }}` | `<main>` 内的 HTML 内容（含 h2 标题和日期） | archetype | `<p>...</p>` |
| `{{ root_path }}` | 相对路径前缀（`/`、`../`、`../../../`） | archetype | `/` |
| `{{ nav_links }}` | 从 `data/config.json` 生成的导航链接 HTML | archetype | `<a href="...">...</a>` |
| `{{ footer_content }}` | 从 `data/config.json` 读取的页脚内容 | archetype | `&copy; 2026 ...` |


> 禁止直接修改模板中的 `{{ 变量 }}` 占位符（除非重构模板系统）。

---

## 内容写作规范（Markdown）

### Front Matter

文章支持可选的 YAML front matter：

```markdown
---
title: 文章标题
date: 8 May. 2026 / 丙午年 癸巳月 壬午日
---

正文...
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 否 | 文章标题，未指定时默认使用文件名 |
| `date` | 否 | 发布日期，未指定时自动生成当前干支日期 |

### 换行语义

- **单换行**：由于启用 `nl2br` 扩展，单个换行符会转换为 `<br />`
- **双换行**：标准 Markdown 段落分隔
- **`<!--sep-->`**：特殊标记，会被替换为 `<br />`，用于需要强制换行但不想分段落的场景

### 代码块

使用围栏代码块并标注语言，以便 Pygments 高亮：

````markdown
```python
def hello():
    print("Hello")
```
````

### 数学公式

支持 KaTeX 渲染：

- 行内：`$...$` 或 `\(...\)`
- 块级：`$$...$$` 或 `\[...\]`

### Obsidian 图片语法

支持 Obsidian 风格的 wiki 链接图片：

```markdown
![[image.jpg]]
![[image.jpg|alt text]]
```

发布时会自动转换为标准 Markdown 并复制图片到文章目录。

---

## 图片与资源处理规范

### 文章配图

- 文章配图应放在 Markdown 源文件**同目录**或**项目根目录**
- 发布时 `build.py` 会自动查找并复制到 `content/{category}/{slug}/`
- 引用路径使用相对路径，如 `![描述](Cat.jpg)`

### 全局图片

- `assets/images/` 仅存放**全站共享**资源（如 `avatar.png`）
- 禁止在 `assets/images/` 中存放文章专属配图

### 远程图片

- 支持外部 URL（`http://`、`https://`、`data:`）
- 远程图片不会被下载或缓存，直接保留原链接

### 图片缺失行为

发布时若引用的本地图片不存在，`build.py` 会打印警告但继续生成 HTML。

### 格式建议

- Web 场景优先使用 JPG/PNG
- 大体积图片（>1MB）建议压缩后再放入项目
- 字体文件放 `assets/fonts/`，图标放 `assets/icons/`

---

## 路径与链接规范

### 汇总页条目格式

`build.py` 自动生成的汇总页条目结构：

```html
<li>
    <a href="../content/{category}/{slug}/index.html">{title}</a>
    <p class="article-date">{date}</p>
</li>
```

### 跨文章链接

- 跨文章链接建议使用**根相对路径**：`/content/{category}/{slug}/index.html`
- 避免使用依赖当前文件层级的相对路径（如 `../../`），以防止路径漂移

### 导航链接更新

- 修改导航结构请编辑 `data/config.json` 的 `nav` 数组，然后运行 `python build.py --build-all`
- `--build-all` 会自动同步所有页面的导航链接和页脚内容
- 快速验证：`python build.py --check-archetypes`

### CSS 路径规则

- `style.css` 必须始终从**项目根目录**引用
- 禁止将 `style.css` 复制到子目录或改用多个副本

---

## CSS 结构与命名规范

### 文件组织逻辑

`style.css` 按以下顺序分组，自上而下阅读即可理解整体架构：

| 文件 | 内容 | 说明 |
|------|------|------|
| `fonts.css` | 字体定义 | Source Code Pro；`style.css` 依次引入 LXGW Bright 的 `subset.css`（优先）和 `result.css`（分包兜底） |
| `variables.css` | CSS 变量 + 暗色模式 | 颜色、背景、边框等全局 Token，含 `@media (prefers-color-scheme: dark)` 覆盖 |
| `prism.css` | 代码高亮暗色主题 | Pygments token 配色（暗色模式），包裹在 `prefers-color-scheme: dark` 中 |
| `base.css` | 全局重置与动画 | `box-sizing`, 字体栈, flex 列布局, `fade-in` 动画 |
| `header.css` | 侧边栏 | 桌面端 3/16 宽度（`min-width: 150px`），桌面 fixed / 短视口 absolute，导航链接样式，含短视口媒体查询 |
| `menu.css` | 竖屏汉堡菜单覆盖层 | `@media (max-width: 649px)`：全屏菜单本体（淡入淡出、可滚动）、菜单内关闭按钮/头像/站点标题、菜单链接样式 |
| `main.css` | 主内容区 | 与侧栏对齐（`margin-left: max(3/16, 150px)`），常规文档流样式（段落、列表、表格、图片） |
| `components.css` | 组件样式 | `.link-list`、`.post-date`、`.signature` |
| `code.css` | 代码与数学公式 | 代码块背景、行内 code 高亮、KaTeX 溢出处理 |
| `footer.css` | 页脚 | 与 main 同宽对齐 |
| `responsive-portrait.css` | 竖屏模式 | `max-width: 649px`：顶栏、正文与页脚的竖屏布局（汉堡菜单见 `menu.css`） |

### 短视口模式（替代原宽屏模式）

桌面模式下视口高度低于 670px 时，固定侧栏（约 675–705px 高）底部导航会被裁切。原宽屏模式（`responsive-wide.css`）已删除，由 `header.css` 末尾的媒体查询（`min-width: 650px and max-height: 669px`）接管：将 `header` 改为 `position: absolute` 随页面整体滚动，使底部导航可以滚动露出。侧栏不再固定，滚动后滑出屏幕（不钉住）。

### 布局系统

采用 **16 列固定比例网格**：

- `header` 宽度：`calc(100% / 16 * 3)`（18.75%），`min-width: 150px`
- `main` / `footer` 左外边距：`max(calc(100% / 16 * 3), 150px)`——与侧栏实际宽度对齐（窄视口下侧栏受 `min-width` 限制时，`main`/`footer` 随之右移）
- `main` / `footer` 宽度：`calc(100% - 左外边距)`，与侧栏并排无重叠

> 修改布局比例时，需同步调整 `header`、`main`、`footer` 三处的 `width` 与 `margin-left`。

### 颜色变量体系

所有颜色通过 `:root` CSS 变量管理，暗色模式在 `@media (prefers-color-scheme: dark)` 中统一覆盖变量值，不直接覆盖具体选择器。

| 变量前缀 | 用途 |
|---------|------|
| `--bg-*` | 背景色（primary、sidebar、code） |
| `--border-*` | 边框色（sidebar、list） |
| `--text-*` | 文本色（primary、nav、body、muted、link） |
| `--text-*-hover` | 悬停色（sidebar、list） |

> 悬停色 `--text-sidebar-hover` 在亮暗模式下均为 `#4aa9c5`（青蓝）。暗色砖红 `#b5563a` 仅用于脚注链接（`components.css` 中的 `.footnote-ref`/`.footnote-backref`，硬编码例外）。
>
> 例外：脚注链接与 `prism.css`（代码高亮 token）使用硬编码颜色，不经过 CSS 变量。

### 类名命名规则

| 类名 | 用途 | 所在位置 |
|------|------|---------|
| `.header-bar` | 头部导航栏容器（桌面端 `display: contents`，移动端恢复 flex） | `header` 内部 |
| `.current-section` | 当前章节链接（跳转本章节导航页），仅移动端显示；首页与汇总页（`body.section-page`）隐藏 | `.header-bar` 内 |
| `.section-page` | 非文章页标记（首页与汇总页的 body 类），用于竖屏下隐藏 current-section 并保持菜单按钮位置 | `body` |
| `.nav-toggle-btn` / `.nav-toggle` | 移动端汉堡菜单（纯 CSS checkbox hack） | `.header-bar` 内 / 同级 |
| `.nav-la` | 导航 Latin 标签 | `nav a` 内部 |
| `.post-date` | 文章页日期行 | `main` 内，紧跟 `h2` |
| `.article-date` | 汇总页文章列表中的日期 | `ul li` 内 |
| `.signature` | 首页签名/引言 | `main` 内 |
| `.arithmatex` / `.katex-display` | 数学公式溢出处理 | 文章页 KaTeX 容器 |
| `.token.*` | 代码高亮（Prism.js 兼容） | 暗色模式覆盖 |

### 动画层级

在 `prefers-reduced-motion: no-preference` 下，内容按以下顺序依次淡入，形成级联效果：

1. `main` — 0.04s 延迟
2. `main h2, main h3, main h4, main h5, main h6` — 0.08s 延迟
3. `main p, ul, table, ol, pre, blockquote` — 0.16s 延迟
4. `footer` — 0.24s 延迟

> 修改动画时需注意层级延迟关系，保持视觉节奏。

### 模式总览（二维象限分割）

当前生效的三条规则以宽度 650px 和高度 670px 为轴：

```
               宽度 650px
              ───────┬─────────
                     │
     竖屏            │    桌面
  (顶栏+汉堡菜单)    │  (固定侧栏)
  宽度 < 650px       │  宽度 ≥ 650px
  不论高度           │  高度 ≥ 670px
                     │
                     ├─────────
                     │  短视口
                     │  (随页滚动侧栏)
                     │  宽度 ≥ 650px
                     │  高度 < 670px
```

（历史四象限：宽度 1005px 与高度 680px 为轴，宽屏模式与最小模式均已删除。）

### 桌面模式

- 宽度 ≥ 650px 且高度 ≥ 670px 时激活
- 固定侧栏（3/16）+ 正文并排

### 竖屏模式

- **断点**：`max-width: 649px`（宽度 ≤ 649px 时触发，不论高度）
- **导航切换**：使用隐藏的 checkbox（`#nav-toggle`）+ `label` 实现纯 CSS 全屏菜单，无 JavaScript。
- `.header-bar` 在移动端从 `display: contents` 恢复为 `display: flex`，承载标题、当前章节链接（`.current-section`，指向本章节导航页）、菜单按钮的横向排列（竖屏下顶栏不显示头像）。
- **首页与汇总页**（`body.section-page`）：不显示 `.current-section`，菜单按钮通过 `margin-left: auto` 保持右侧位置。
- **汉堡菜单**（规则位于 `menu.css`，布局变量见 `variables.css` 的 `--menu-*`）：打开时 `header-bar` 隐藏，关闭按钮（≡）移至菜单右上角；菜单内依次为头像（`--menu-avatar-top: 4rem`）、站点标题（`--menu-title-top: 11rem`）、导航链接（`--menu-links-top: 15rem` 起）。菜单为全屏覆盖层（`100dvh`、`overflow-y: auto`），内容随菜单滚动，整体 0.2s 淡入淡出。

### 短视口模式

- **断点**：`min-width: 650px` 且 `max-height: 669px`（宽度 ≥ 650px 且高度 ≤ 669px 时触发）
- 即桌面模式的矮视口分支：侧栏由 `position: fixed` 改为 `position: absolute` 随页面整体滚动，底部导航可滚动露出（不钉住）
- 与桌面模式共享分割线、导航居中、下划线样式（见 `header.css` 的 `min-width: 650px` 块）

### 修改 CSS 时的注意事项

1. **变量优先**：新增颜色应先在 `:root` 中定义变量，再在暗色模式中覆盖，最后在选择器中使用。
2. **布局联动**：修改侧边栏宽度时，必须同步修改 `main` 和 `footer` 的 `margin-left` 与 `width`。
3. **模式覆盖**：桌面/短视口/竖屏三模式互斥（以宽度 650px 为轴、高度 670px 分支），新增媒体查询时注意不要破坏此结构。
4. **动画尊重**：新增动画应包裹在 `@media (prefers-reduced-motion: no-preference)` 中，保证可访问性。
5. **避免直接修改 `.token.*`**：代码高亮类名由 Prism.js 生成，暗色模式覆盖即可，无需新增选择器。

---

## 模板一致性维护规范

### 何时运行

以下情况应运行模板一致性检查：

- 修改 `data/config.json`（nav、footer）后
- 修改 `archetypes/archetype.html` 后
- 新增或删除分类后
- 发现页面布局或样式异常时

**推荐使用一键全量构建覆盖所有检查：**
```bash
python build.py --build-all
```

该命令依次执行：全站模板同步 → 模板一致性检查。

### 检查范围

`templint.py` 会扫描以下位置的 `.html` 文件：

- 根目录 `*.html`
- `pages/*.html`
- `content/**/*.html`
- `archetypes/archetype.html`

### 检查内容

对照 `data/config.json` 验证每个文件：

| 检查项 | 说明 |
|--------|------|
| doctype | 必须为 `<!doctype html>` |
| 语言属性 | 与 `data/config.json` 的 `html_lang` 一致 |
| charset | `<meta charset="UTF-8" />` |
| viewport | `<meta name="viewport" ...>` |
| CSS 链接 | 包含 `data/config.json` 中 `css_file` 定义的文件 |
| title 格式 | 必须含 `| {site.title}`（从 `data/config.json` 读取） |
| header 结构 | 包含头像、博客标题、导航切换按钮 |
| nav 链接 | 链接目标与文字必须与 `data/config.json` 中 `nav` 定义一致 |
| footer 内容 | 必须与 `data/config.json` 中 `footer` 字段一致 |

### 自动重建（Shell 同步）

检查发现问题时，可用当前模板 + 当前数据重建文件：

1. **交互模式**（默认）：逐个询问是否重建每个问题文件
2. **自动模式**：`python build.py --check-archetypes -y`

**全站强制同步**（跳过问题诊断，直接全部重建）：
```bash
python build.py --rebuild -y
```

### 重建保护机制

`rebuild_from_base()` 重建时会保留以下内容：

- `<main>` 标签内的所有内容（文章正文 + h2 标题 + 日期）
- 页面标题（从 `<title>` 中提取后填入 `{{ title }}`）
- 使用 `{{ root_path }}` 变量自动根据文件深度设置相对路径前缀
- `archetypes/` 下的模板文件始终跳过，不会被写入覆盖

> 重建后建议运行 `python build.py --check-archetypes` 验证一致性。

---

## 爬虫规则（robots.txt）

`robots.txt` 位于项目根目录，部署后对应 `https://Tritium79.github.io/robots.txt`。

当前规则：**仅允许爬虫抓取首页**（`/` 和 `index.html`），其余路径全部 `Disallow`：

| 屏蔽路径 | 说明 |
|---------|------|
| `/content/` | 所有文章内容页 |
| `/pages/` | 所有汇总页 |
| `/assets/` | 静态资源 |
| `/build/` | 构建脚本 |
| `/data/` | 配置数据 |
| `/archetypes/` | 模板文件 |

### 何时更新

- 新增**顶级目录**（如 `photos/`）且不希望被爬取时，需在 `robots.txt` 中追加 `Disallow: /新目录/`
- 在 `content/`、`pages/`、`assets/` 等已有 `Disallow` 路径下新增文件**无需**更新
- 如需开放某个目录的爬取，删除对应 `Disallow` 行即可

---

## 禁止事项

- 禁止在内容目录或 pages 目录外创建 `.html` 文件
- 禁止直接修改模板中的 `{{ 变量 }}` 占位符（除非重构模板系统）
- 禁止在静态资源目录中存放非资源类文件
