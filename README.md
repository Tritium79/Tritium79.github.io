# Tritium79's Blog

静态个人博客，使用 HTML + CSS。使用自制Python脚本管理。

> **注意：** 本 README.md 应随目录结构变化而更新，反映最新结构。它是一份可变参考文档，而非静态档案。
>
> **快速上手 → 见 [README_Simplified.md](README_Simplified.md)**

---

## 目录结构

```
Tritium79.github.io/
├── index.html                  # 首页
├── style.css                   # 全局样式
│
├── assets/                     # 全局静态资源
│   ├── css/                    # 附加 CSS
│   ├── fonts/                  # 字体文件
│   ├── icons/                  # 图标
│   └── images/                 # 图片资源
│
├── content/                    # 文章
│   ├── tabularium/             # 存档 / Tabularium
│   │   └── {Article-Slug}/
│   │       ├── index.html      # 生成的页面
│   │       ├── index.md        # 源 Markdown（图片路径已本地化）
│   │       └── (附属资源，如图片)
│   ├── commentarii/            # 记录 / Commentarii
│   │   └── {Article-Slug}/
│   │       ├── index.html
│   │       ├── index.md
│   │       └── (附属资源)
│   ├── sylvae/                 # 随笔 / Sylvae
│   │   └── {Article-Slug}/
│   │       ├── index.html
│   │       ├── index.md
│   │       └── (附属资源)
│   └── interpretationes/       # 译文 / Interpretationes
│       └── {Article-Slug}/
│           ├── index.html
│           ├── index.md
│           └── (附属资源)
│
├── pages/                      # 章节
│   ├── tabularium.html         # 存档/Tabularium
│   ├── commentarii.html        # 记录 / Commentarii
│   ├── deme.html               # 关于 / De Me
│   ├── amici.html              # 友链 / Amici
│   ├── sylvae.html             # 随笔 / Sylvae
│   └── interpretationes.html   # 译文 / Interpretationes
│
├── build/                    # 构建脚本
│   ├── build.py                # 入口：CLI 参数解析 + 交互菜单
│   ├── build.sh                # Shell 封装（激活 venv 后运行 build.py）
│   ├── config.py               # 常量：路径、分类定义（从 data/ 加载）
│   ├── data_loader.py          # 数据加载：从 data/*.json 读取配置
│   ├── content.py              # 内容生成：Markdown 渲染、图片处理、文章发布
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
├── .gitignore                  # Git 忽略规则
├── README.md                   # 目录结构与命名规范
└── AGENTS.md                   # AI 辅助审查指令
```

---

## 命名规则

### 章节（category）

| 章节名              | 中文名  | 拉丁文名   |
|--------------------|-------|-----------|
| `sylvae`           | 随笔   | Sylvae    |
| `commentarii`      | 记录   | Commentarii |
| `interpretationes` | 译文   | Interpretationes |
| `tabularium`       | 存档   | Tabularium |

新增章节需同时在 `data/categories.json` 和 `data/config.json` 的 `nav` 中注册，并在 `pages/` 下创建对应的 `.html` 汇总页。

### 文章文件夹（slug）

- 每个文章一个独立文件夹，统一使用 `index.html` 作为入口文件
- 文件夹名使用 slug 命名：单词首字母大写、其余字母小写、单词间以连字符 `-` 分隔
- 允许全大写缩写（如 `OA`、`HDR`、`LaTeX` 等专有名词保留原写法）
- 仅允许字母、数字、汉字、连字符
- 示例：`OA-Introduction-Translation`、`Cat-Record`、`Blog-Init`、`Code-LaTeX-HDR-Test`

### 附属资源

- 文章附属图片、文件等放置在同一文章文件夹内
- 引用路径使用相对路径（如 `Cat.jpg`）

### 汇总页

- `pages/{category}.html` — 按分类列出文章标题与日期
- 新增文章时，`build.py` 会自动在对应汇总页的 `<ul>` 中追加条目
- 仅当文章被真正删除时才手动移除对应条目

### 构建脚本

- `build/build.py` — 主构建脚本
- 工作流：Markdown 文件 → 解析 front matter → 渲染 HTML → 写入 `content/{category}/{slug}/index.html`（同时复制源 `.md` 并本地化图片路径） → 更新汇总页
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
  9. Git
```

- 所有功能支持 `q` 中途退出
- `python build.py --check-archetypes` — 对照 `data/config.json` 检查所有 HTML 文件的结构一致性（nav、footer 等），可选自动修复
- `python build.py --rebuild` — 全站 Shell 同步：用当前模板（archetype.html）+ 数据（data/config.json）重建所有页面
- `python build.py --build-all` — 一键全量：rebuild → check-archetypes
- `python build.py --list-cat sylvae` — 非交互式列出指定分类文章
- `python build.py --delete-by sylvae Slug-Name -y` — 非交互式删除文章
- `python build.py --retitle-by sylvae Slug-Name -t "新标题" -d "新日期"` — 非交互式修改标题/日期
- `python build.py --git` — Git 提交与推送
- `python build.py --lunar-date` — 获取当前干支日期
- 所有路径以项目根目录为基准
- Markdown 渲染扩展由 `data/settings.json` 的 `markdown_extensions` 定义
- 发布文章时日期留空，默认使用当前干支日期（格式由 `data/settings.json` 的 `date_format` 定义）

### assets

- `fonts/` — 存放字体文件
- `icons/` — 存放图标文件
- `css/` — 附加样式表
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
        {"href": "index.html", "cn": "首页", "la": "Domus"},
        {"href": "pages/sylvae.html", "cn": "随笔", "la": "Sylvae"}
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
| `nav` | 导航链接数组，每项含 `href`/`cn`/`la` | 运行 `--build-all` |

### data/settings.json

构建过程设置（Markdown 渲染、日期格式、文件管理器等），详见 `build/README.md`。



---

## 分类/章节扩展规范

新增分类需完成以下步骤：

1. **注册分类**：在 `data/categories.json` 中添加一条：
   ```json
   "your-key": {
       "name": "中文 / Latin",
       "section_cn": "中文",
       "page": "pages/your-key.html"
   }
   ```

2. **更新导航**：在 `data/config.json` 的 `nav` 数组中添加对应条目

3. **创建汇总页**：在 `pages/` 下创建 `{key}.html`，结构如下：
   ```html
   <main>
       <h2>中文名</h2>
       <p>描述...</p>
       <hr />
       <ul class="link-list">
           <!-- build.py 会自动在此处追加文章条目 -->
       </ul>
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

### 导航双语格式

导航链接必须使用以下结构，不得更改：

```html
<a href="...">
    <span class="nav-cn">中文</span>
    <span class="sep">/</span>
    <span class="nav-la">Latin</span>
</a>
```

### 模板变量系统

`archetypes/archetype.html` 使用以下模板变量：

| 变量 | 用途 | 适用范围 | 示例值 |
|------|------|---------|--------|
| `{{ title }}` | 页面标题 `<title>` | base + article | `序` |
| `{{ section }}` | 当前章节名（nav-current / current-section） | base + article | `随笔` |
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

| 区块 | 内容 | 说明 |
|------|------|------|
| `@font-face` | 字体定义 | LXGW Bright、Source Code Pro |
| `:root` | CSS 变量 | 颜色、背景、边框等全局 Token |
| `@media (prefers-color-scheme: dark)` | 暗色模式覆盖 | 对 `:root` 变量的完整重写 + Prism token 配色 |
| `*` / `html` / `body` | 全局重置与基础 | `box-sizing`, 字体栈, flex 列布局 |
| `@keyframes` / `prefers-reduced-motion` | 动画定义 | `fade-in` 及分层级联动画 |
| `header` | 固定侧边栏 | 桌面端 7/32 宽度，fixed 定位 |
| `main` | 主内容区 | 桌面端 25/32 宽度，常规文档流样式 |
| `footer` | 页脚 | 与 main 同宽对齐 |
| `pre` / `code` / `.arithmatex` | 代码与数学公式 | 代码块背景、行内 code 高亮、KaTeX 溢出处理 |
| `@media (max-width: 1004px)` | 竖屏/最小模式响应式 | 宽度不足时触发 |

### 布局系统

采用 **32 列固定比例网格**：

- `header` 宽度：`calc(100% / 32 * 7)`（约 21.875%）
- `main` / `footer` 宽度：`calc(100% / 32 * 25)`（约 78.125%）
- `main` 左外边距与 `header` 宽度相等，形成并排列

> 修改布局比例时，需同步调整 `header`、`main`、`footer` 三处的 `width` 与 `margin-left`。

### 颜色变量体系

所有颜色通过 `:root` CSS 变量管理，暗色模式在 `@media (prefers-color-scheme: dark)` 中统一覆盖变量值，不直接覆盖具体选择器。

| 变量前缀 | 用途 |
|---------|------|
| `--bg-*` | 背景色（primary、sidebar、code） |
| `--border-*` | 边框色（sidebar、list） |
| `--text-*` | 文本色（primary、nav、body、muted、link） |
| `--text-*-hover` | 悬停色（sidebar、list） |

> 亮色模式悬停色为 `#4aa9c5`（青蓝），暗色模式为 `#b5563a`（砖红），形成视觉反差。

### 类名命名规则

| 类名 | 用途 | 所在位置 |
|------|------|---------|
| `.header-bar` | 头部导航栏容器（桌面端 `display: contents`，移动端恢复 flex） | `header` 内部 |
| `.current-section` | 当前页面标题，仅移动端显示 | `.header-bar` 内 |
| `.nav-toggle-btn` / `.nav-toggle` | 移动端汉堡菜单（纯 CSS checkbox hack） | `.header-bar` 内 / 同级 |
| `.nav-cn` / `.nav-la` / `.sep` | 导航双语标签与中英文分隔符 | `nav a` 内部 |
| `.post-date` | 文章页日期行 | `main` 内，紧跟 `h2` |
| `.article-date` | 汇总页文章列表中的日期 | `ul li` 内 |
| `.article-meta` | 文章元信息容器 | `main` 内（build.py 生成） |
| `.signature` | 首页签名/引言 | `main` 内 |
| `.arithmatex` / `.katex-display` | 数学公式溢出处理 | 文章页 KaTeX 容器 |
| `.token.*` | 代码高亮（Prism.js 兼容） | 暗色模式覆盖 |

### 动画层级

在 `prefers-reduced-motion: no-preference` 下，内容按以下顺序依次淡入，形成级联效果：

1. `main` — 0.04s 延迟
2. `main h2, main h3` — 0.08s 延迟
3. `main p, ul, table, ol, pre, blockquote` — 0.16s 延迟
4. `footer` — 0.24s 延迟

> 修改动画时需注意层级延迟关系，保持视觉节奏。

### 模式总览（二维象限分割）

四条模式以宽度 1005px 和高度 680px 为轴，互斥无重叠：

```
               宽度 1005px
              ───────┬───────
                     │
     竖屏            │    桌面
  (顶栏+汉堡菜单)    │  (固定侧栏)
  高度 ≥ 680px       │  高度 ≥ 680px
                     │
  ──────────────────┼──────────────────
                     │
     最小            │    宽屏
  (可滚动顶栏+嵌入)  │  (固定顶栏+展开)
  高度 < 680px       │  高度 < 680px
                     │
```

### 桌面模式

- 默认模式，无媒体查询条件
- 宽度 ≥ 1005px 且高度 ≥ 680px 时激活（即不满足其他三种模式时自动生效）

### 竖屏模式

- **断点**：`max-width: 1004px` 且 `min-height: 680px`（宽度 ≤ 1004px 且高度 ≥ 680px 时触发）
- **导航切换**：使用隐藏的 checkbox（`#nav-toggle`）+ `label` 实现纯 CSS 全屏菜单，无 JavaScript。
- `.header-bar` 在移动端从 `display: contents` 恢复为 `display: flex`，承载头像、标题、菜单按钮的横向排列。

### 宽屏模式

- **断点**：`min-width: 1005px` 且 `max-height: 679px`（宽度 ≥ 1005px 且高度 ≤ 679px 时触发）
- 侧栏（`header`）变为固定顶栏，头像缩小，博客标题与导航链接水平排列
- 导航按钮全部展开在顶栏上，隐藏汉堡菜单按钮和当前章节标记
- `main` 内容区取消左侧边距，铺满全宽，左右内边距增大至 `12rem`
- 标题、日期、正文居中对齐
- 图片铺满整个内容区宽度（`width: 100%`），无最大高度限制，保持原始比例

### 最小模式

- **触发器**：`max-width: 1004px` 且 `max-height: 679px`（宽度 ≤ 1004px 且高度 ≤ 679px 时触发）
- 基于竖屏布局，但顶栏不再是固定定位 + 全屏菜单覆盖层
- `header` 变为 `position: relative`，随页面滚动（可滑走）
- 隐藏汉堡菜单按钮和当前章节标记
- 导航链接展开嵌入在顶栏下方（竖排，中文/拉丁文上下排列），与竖屏全屏菜单样式一致但处于正常文档流中
- `main` 内容区铺满全宽，简化内边距，文字左对齐

### 修改 CSS 时的注意事项

1. **变量优先**：新增颜色应先在 `:root` 中定义变量，再在暗色模式中覆盖，最后在选择器中使用。
2. **布局联动**：修改侧边栏宽度时，必须同步修改 `main` 和 `footer` 的 `margin-left` 与 `width`。
3. **模式覆盖**：四种模式互斥（基于宽度/高度二维分割），新增媒体查询时注意不要破坏此结构。
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

## 禁止事项

- 禁止在内容目录或 pages 目录外创建 `.html` 文件
- 禁止直接修改模板中的 `{{ 变量 }}` 占位符（除非重构模板系统）
- 禁止在静态资源目录中存放非资源类文件
