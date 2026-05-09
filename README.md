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
├── assets/                     # 静态资源
│   ├── css/                    # 附加 CSS（预留，当前为空）
│   ├── fonts/                  # 字体文件
│   ├── icons/                  # 图标（预留，当前为空）
│   └── images/                 # 图片资源（如 avatar.png）
│
├── content/                    # 文章内容
│   ├── archivum/               # 存档 / Archivum
│   │   └── {article-slug}/
│   │       └── index.html
│   ├── commentarii/            # 记录 / Commentarii
│   │   └── {article-slug}/
│   │       ├── index.html
│   │       └── (附属资源，如 图片)
│   ├── silvae/                 # 随笔 / Silvae
│   │   └── {article-slug}/
│   │       └── index.html
│   └── versiones/              # 译文 / Versiones
│       └── {article-slug}/
│           └── index.html
│
├── pages/                      # 分类汇总页
│   ├── archivum.html
│   ├── commentarii.html
│   ├── deme.html               # 关于 / De Me
│   ├── nexus.html              # 友链 / Nexus
│   ├── silvae.html
│   └── versiones.html
│
├── scripts/                    # 构建工具
│   ├── build.py                # 入口：CLI 参数解析 + 交互菜单
│   ├── build.sh                # Shell 封装（激活 venv 后运行 build.py）
│   ├── config.py               # 常量：路径、分类定义、模板
│   ├── content.py              # 内容生成：Markdown 渲染、图片处理、文章发布
│   ├── management.py           # 文章管理：列表、删除、文件管理器、修改标题/日期
│   ├── utils.py                # 工具函数：slugify、ask、confirm、front matter 解析
│   ├── requirements.txt        # Python 依赖
│   ├── README.md               # 脚本文档
│   └── venv/                   # Python 虚拟环境
│
├── template/                   # 文章 HTML 模板
│   └── article.html
│
├── data/                       # 数据文件（预留，当前为空）
│
├── README.md                   # 本文件 — 目录结构与命名规范
└── AGENTS.md                   # AI 辅助审查指令
```

---

## 命名规则

### 分类（category）

| 目录名       | 中文名 | 拉丁文名   |
|-------------|--------|-----------|
| `silvae`    | 随笔   | Silvae    |
| `commentarii` | 记录 | Commentarii |
| `versiones` | 译文   | Versiones |
| `archivum`  | 存档   | Archivum |

新增分类必须同时在 `scripts/build.py` 的 `CATEGORIES` 和 `SECTION_MAP` 中注册，并在 `pages/` 下创建对应的 `.html` 汇总页。

### 文章文件夹（slug）

- 每个文章一个独立文件夹，统一使用 `index.html` 作为入口文件
- 文件夹名使用 slug 命名：单词首字母大写、其余字母小写、单词间以连字符 `-` 分隔
- 仅允许字母、数字、汉字、连字符
- 示例：`OA-Introduction-Translation`、`Cat-Record`、`Blog-Init`

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
- 所有路径以项目根目录为基准

### assets

- `fonts/` — 仅存放字体文件（`.ttf`、`.woff2` 等）
- `icons/` — 仅存放图标文件（`avatar.png` 等）
- `css/` — 附加样式表（当前为空）
- `images/` — 通用图片资源（当前为空）

---

## 禁止事项

- 禁止在内容目录或 pages 目录外创建 `.html` 文件
- 禁止直接修改 `template/article.html` 中的 `{{ 变量 }}` 占位符（除非重构模板系统）
- 禁止在静态资源目录中存放非资源类文件
