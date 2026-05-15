# AGENTS.md — 给 opencode 的指令

## 职责

以 `README.md` 为权威参考，审查项目目录结构和命名规范的一致性。

---

## 审查流程

### 1. 读取参照

读取 `README.md`，理解当前声明的目录结构和命名规则。

### 2. 审查目录结构

将实际目录与 README.md 中描述的目录结构逐层对比：

- 有无未在 README 中记录的目录或文件？
- 有无在 README 中存在但实际已不存在的目录或文件（需先确认是否应删除）？
- `content/{category}/` 下的分类是否与 `build/build.py` 中 `CATEGORIES` 的定义一致？
- 汇总页 `pages/{category}.html` 是否与 `content/{category}/` 下的文章对应？

### 3. 审查命名规范

对照 README.md 中的命名规则逐条检查：

- 文章文件夹名是否符合 slug 规则（单词首字母大写、连字符分隔、无非法字符）？
- 文章入口是否统一使用 `index.html`？
- `assets/` 子目录中的文件类型是否与对应目录用途一致？
- `build/` 外是否有无关的可执行脚本？
- `archetypes/` 中是否只有模板文件？

### 4. 发现差异时

**必须使用 `question` 工具**向用户报告每一项差异，并提供选项：

- 选项一：以 README.md 为准，修改实际目录/文件
- 选项二：以实际目录为准，更新 README.md
- 选项三：跳过此项

**在用户明确同意之前，不得做任何修改。**

### 5. 审查隐私安全

检查以下隐私风险，发现问题时同样用 `question` 工具报告：

- `.env`、`credentials.json`、`config.yml` 等可能包含密钥或凭据的文件是否被追踪？
- HTML 中是否暴露了个人信息、密码、API密钥 等敏感信息？
- 图片元数据中是否可能包含 GPS 位置等隐私信息（提醒用户自行检查，不要自动处理）？
- `.gitignore` 是否覆盖了常见隐私文件？

**禁止对包含潜在隐私内容的文件进行自动编辑或自动提交。**

### 6. 审查版权

检查以下版权风险，发现问题时用 `question` 工具报告：

- 译文是否标注了原作者、原作品名称及出处？
- 使用的图片、字体等资源是否具有合法授权或属于合理使用范畴？
- 代码、引文等第三方内容是否标注了来源？
- 文章内容本身是否侵犯他人著作权？

---

## 优先使用构建脚本

本博客配备了一套完整的 Python 构建工具 `build/build.py`。**涉及全站修改时，优先调用构建脚本，而非直接编辑 HTML 文件。**

### 构建脚本能做什么

| 操作 | 命令 |
|------|------|
| 改导航/页脚/站点标题 | 编辑 `data/config.json` → `python build.py --build-all` |
| 发布文章 | `python build.py -f article.md -c sylvae -y` |
| 列出文章 | `python build.py --list-cat sylvae` |
| 删除文章 | `python build.py --delete-by sylvae Slug-Name -y` |
| 修改文章标题/日期 | `python build.py --retitle-by sylvae Slug-Name -t "新标题" -d "日期"` |
| 全站模板同步 | `python build.py --rebuild -y` |
| 模板一致性检查 | `python build.py --check-archetypes` |
| Git 提交推送 | `python build.py --git` |

### 执行策略

1. **遇到全站修改需求**（改 footer、nav、站点标题等）：编辑 `data/config.json`，调用 `python build.py --build-all`
2. **遇到文章管理需求**（发/删/改文章）：直接调用 `python build.py` 的 CLI 命令
3. **只有构建脚本不支持的场景**（如修改 CSS 样式、修改模板结构、新增分类等），才考虑直接编辑 HTML/Python 文件
4. 所有 `build.py` 命令必须通过 `bash build/build.sh` 或 `python build.py` 在项目根目录执行

---

## 禁止执行的命令

以下命令**绝对禁止**执行，除非用户单独以自然语言明确要求：

- `git push --force` / `git push -f`（除非用户明确说 "force push"）
- `git reset --hard` / `git reset HEAD~` 等破坏性操作
- `rm -rf`、`rm -r` 等危险删除命令
- 修改 `.git/config` 或全局 git 配置
- 安装或更新系统级软件包
- 扫描或修改项目外的文件

---

## 更新 README.md 的时机

当以下情况发生时，应主动提醒用户 README.md 需要更新：

- 新增或删除了分类
- 添加了新的顶层目录或改变了目录结构
- 命名规则发生了调整
- 构建脚本新增了核心功能或 CLI 命令
