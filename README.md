# Tritium79's Blog

静态个人博客，无框架，纯 HTML + CSS。使用 Python 脚本将 Markdown 发布为 HTML。

> **注意：** 本 README.md 应随目录结构变化而更新，反映最新结构。它是一份可变参考文档，而非静态档案。

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
│   ├── archivum/               # 存档 / Archivum
│   │   └── {Article-Slug}/
│   │       ├── index.html
│   │       └── (附属资源，如 图片)
│   ├── commentarii/            # 记录 / Commentarii
│   │   └── {Article-Slug}/
│   │       ├── index.html
│   │       └── (附属资源，如 图片)
│   ├── silvae/                 # 随笔 / Silvae
│   │   └── {Article-Slug}/
│   │       ├── index.html
│   │       └── (附属资源，如 图片)
│   └── versiones/              # 译文 / Versiones
│       └── {Article-Slug}/
│           ├── index.html
│           └── (附属资源，如 图片)
│
├── pages/                      # 章节
│   ├── archivum.html           # 存档/Archivum
│   ├── commentarii.html        # 记录 / Commentarii
│   ├── deme.html               # 关于 / De Me
│   ├── nexus.html              # 友链 / Nexus
│   ├── silvae.html             # 随笔 / Silvae
│   └── versiones.html          # 译文 / Versiones
│
├── scripts/                    # 构建脚本
│   ├── build.py                # 入口：CLI 参数解析 + 交互菜单
│   ├── build.sh                # Shell 封装（激活 venv 后运行 build.py）
│   ├── config.py               # 常量：路径、分类定义、模板
│   ├── content.py              # 内容生成：Markdown 渲染、图片处理、文章发布
│   ├── management.py           # 文章管理：列表、删除、文件管理器、修改标题/日期
│   ├── utils.py                # 工具函数：slugify、ask、confirm、front matter 解析
│   ├── templint.py             # 模板一致性检查：对比所有 HTML 与 base.html
│   ├── git_ops.py              # Git 提交与推送
│   ├── requirements.txt        # Python 依赖
│   ├── README.md               # 脚本文档
│   └── venv/                   # Python 虚拟环境
│
├── template/                   # HTML 模板
│   ├── article.html            # 文章页模板（含 KaTeX，供 build.py 使用）
│   └── base.html               # 通用页面模板（根相对路径，供手动页面使用）
│
├── data/                       # 数据
│
├── .gitignore                  # Git 忽略规则
├── README.md                   # 目录结构与命名规范
└── AGENTS.md                   # AI 辅助审查指令
```

---

## 命名规则

### 章节（category）

| 章节名       | 中文名 | 拉丁文名   |
|-------------|--------|-----------|
| `silvae`    | 随笔   | Silvae    |
| `commentarii` | 记录 | Commentarii |
| `versiones` | 译文   | Versiones |
| `archivum`  | 存档   | Archivum |

新增章节必须同时在 `scripts/` 下脚本的 `CATEGORIES` 和 `SECTION_MAP` 中注册，并在 `pages/` 下创建对应的 `.html` 汇总页。

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

- `scripts/build.py` — 主构建脚本
- 工作流：Markdown 文件 → 解析 front matter → 渲染 HTML → 写入 `content/{category}/{slug}/index.html` → 更新汇总页
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
  8. Git
```

- 所有功能支持 `q` 中途退出
- `python build.py --check-template` — 对照 `template/base.html` 检查所有 HTML 文件的结构一致性，可选自动修复
- `python build.py --git` — Git 提交与推送
- `python build.py --lunar-date` — 获取当前干支日期
- 所有路径以项目根目录为基准
- Markdown 渲染启用 `nl2br` 扩展，单个换行符转换为 `<br />`
- 发布文章时日期留空，默认使用当前干支日期（格式：`8 May. 2026 / 丙午年 癸巳月 壬午日`）

### assets

- `fonts/` — 存放字体文件
- `icons/` — 存放图标文件
- `css/` — 附加样式表
- `images/` — 通用图片资源

---

## 分类/章节扩展规范

新增分类需完成以下步骤：

1. **注册分类**：在 `scripts/config.py` 中三处注册：
   - `CATEGORIES` — 添加 `(key, '中文 / Latin')` 元组
   - `SECTION_MAP` — 添加 `key: '中文名'` 映射
   - `PAGE_MAP` — 添加 `key: ROOT_DIR / 'pages' / 'key.html'` 映射

2. **创建汇总页**：在 `pages/` 下创建 `{key}.html`，结构如下：
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

3. **创建内容目录**：`content/{key}/`（build.py 发布时会自动创建）

4. **更新导航**：若 `--check-template` 无法自动处理，需手动更新 `template/base.html` 和 `template/article.html` 的 `<nav>` 部分

---

## HTML 模板与结构规范

### 模板分工

| 模板 | 用途 | 路径类型 |
|------|------|---------|
| `template/base.html` | 手动维护的页面（`index.html`、`pages/*.html`） | 根相对路径 `/` |
| `template/article.html` | build.py 生成的文章页 | 相对路径 `../../../` |

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

### 模板变量系统（`article.html`）

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `{{ title }}` | 文章标题 | `序` |
| `{{ date }}` | 发布日期 | `8 May. 2026 / 丙午年 癸巳月 壬午日` |
| `{{ content }}` | Markdown 渲染后的 HTML | `<p>...</p>` |
| `{{ section }}` | 所属分类中文名 | `随笔` |

> 禁止直接修改 `template/article.html` 中的占位符（除非重构模板系统）。

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

- 新增/删除/重命名文章或分类后，运行 `python build.py --check-template`
- 该命令会自动检查所有 HTML 文件的导航链接是否与 `template/base.html` 一致

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
| `@media (max-aspect-ratio: 1/1)` | 移动端响应式 | 以宽高比而非像素宽度作为断点 |

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

### 移动端特殊设计

- **断点**：`max-aspect-ratio: 1/1`（宽高比小于 1:1 时触发），而非传统的 `max-width`。这意味着窄屏横置设备不会进入移动端布局。
- **导航切换**：使用隐藏的 checkbox（`#nav-toggle`）+ `label` 实现纯 CSS 全屏菜单，无 JavaScript。
- `.header-bar` 在移动端从 `display: contents` 恢复为 `display: flex`，承载头像、标题、菜单按钮的横向排列。

### 修改 CSS 时的注意事项

1. **变量优先**：新增颜色应先在 `:root` 中定义变量，再在暗色模式中覆盖，最后在选择器中使用。
2. **布局联动**：修改侧边栏宽度时，必须同步修改 `main` 和 `footer` 的 `margin-left` 与 `width`。
3. **移动端同步**：在 `max-aspect-ratio: 1/1` 媒体查询中，任何对桌面布局的结构性改动都需要检查移动端对应规则。
4. **动画尊重**：新增动画应包裹在 `@media (prefers-reduced-motion: no-preference)` 中，保证可访问性。
5. **避免直接修改 `.token.*`**：代码高亮类名由 Prism.js 生成，暗色模式覆盖即可，无需新增选择器。

---

## 模板一致性维护规范

### 何时运行

以下情况应运行模板一致性检查：

- 修改 `template/base.html` 后
- 新增或删除分类导致导航结构变化后
- 新建手动维护的 HTML 页面后
- 发现页面布局或样式异常时

命令：
```bash
python build.py --check-template
```

### 检查范围

`templint.py` 会扫描以下位置的 `.html` 文件：

- 根目录 `*.html`
- `pages/*.html`
- `content/**/*.html`
- `template/article.html`

### 检查内容

对照 `template/base.html` 验证每个文件：

| 检查项 | 说明 |
|--------|------|
| doctype | 必须为 `<!doctype html>` |
| 语言属性 | `<html lang="zh-CN">` |
| charset | `<meta charset="UTF-8" />` |
| viewport | `<meta name="viewport" ...>` |
| CSS 链接 | 包含 `style.css` |
| title 格式 | 必须含 `| Tritium79's Blog` |
| header 结构 | 包含头像、博客标题、导航切换按钮 |
| nav 链接 | 链接目标与文字必须与 `base.html` 完全一致 |
| footer 内容 | 必须与 `base.html` 一致 |

### 自动重建

检查发现问题时，可选择按 `base.html` 重建：

1. **交互模式**（默认）：逐个询问是否重建每个问题文件
2. **自动模式**：`python build.py --check-template -y` 自动重建所有问题文件

### 重建保护机制

重建时会保留以下内容：

- `<main>` 标签内的所有内容（文章正文）
- `<head>` 中超出 `base.html` 标准的元素（如 KaTeX 的 CSS/JS）
- 页面标题（从 `<title>` 中提取替换 `{{ title }}`）
- 自动根据文件深度调整相对路径（`/` → `../` 或 `../../../`）

> 重建后建议检查手动页面（如 `deme.html`、`nexus.html`）的 `<main>` 内容是否完整。

---

## 禁止事项

- 禁止在内容目录或 pages 目录外创建 `.html` 文件
- 禁止直接修改 `template/article.html` 中的 `{{ 变量 }}` 占位符（除非重构模板系统）
- 禁止在静态资源目录中存放非资源类文件
