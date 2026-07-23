# 博客使用指南

## 快速开始

```sh
cd build
source venv/bin/activate
python3 build.py          # 进入交互菜单
```

---

## 发布文章

写一篇 Markdown：

```markdown
---
title: 文章标题
date: 8 May. 2026 / 丙午年 癸巳月 壬午日
---

正文内容，支持 **加粗**、`代码`、$数学公式$。

![图片描述](图片文件名.jpg)
```

运行：

```
python build.py          # → 选 2. 发布文章
```

按提示输入文件路径、选择分类即可。日期留空自动生成干支日期。

发布后会自动：
- 生成 `content/{分类}/{Slug}/index.html`
- 复制图片到文章文件夹
- 复制源 `.md` 文件到文章文件夹（图片路径已本地化）
- 更新对应汇总页

---

## 修改站点配置

| 想做什么 | 改哪个文件 | 然后运行 |
|---------|-----------|---------|
| 改导航栏/页脚 | `data/config.json` | `python build.py --build-all` |
| 改博客标题 | `data/config.json` → `site.title` | `python build.py --build-all` |
| 首页签名 | 手动编辑 `index.html` | — |
| 关于页内容 | 手动编辑 `pages/deme.html` | — |
| 友链 | 手动编辑 `pages/amici.html` | — |

---

## 新增章节

1. 在 `data/categories.json` 中添加一条
2. 在 `data/config.json` 的 `nav` 中添加对应链接
3. 创建 `pages/{key}.html`（汇总页）
4. 运行 `python build.py --build-all`

---

## 菜单功能一览

```
0. 退出
1. 文章列表        — 按分类查看文章
2. 发布文章        — 从 Markdown 发布新文章
3. 删除文章        — 删除文章及汇总页条目
4. 修改标题        — 修改文章标题/日期
5. 管理目录        — 文件管理器（重命名/移动/删除）
6. 检查模板        — 检查全站 HTML 结构一致性
7. 获取日期        — 生成干支日期
8. 重建页面        — 根据模板重建所有页面
9. Git             — 提交并推送
```

所有操作支持 `q` 中途退出。

---

## CLI 命令（不用菜单）

```sh
python build.py -f article.md -c sylvae                    # 直接发布
python build.py --build-all                                # 全站重建+检查
python build.py --check-archetypes                         # 只检查一致性
python build.py --list-cat sylvae                          # 列出分类文章
python build.py --delete-by sylvae Slug-Name -y            # 删除文章
python build.py --retitle-by sylvae Slug-Name -t "新标题"   # 改标题
python build.py --git                                      # Git 提交推送
python build.py --lunar-date                               # 干支日期
```

---

## 目录结构

```
data/               ← 配置文件都在这里
├── config.json     — 站点设置（标题、导航、页脚、语言）
├── categories.json — 章节定义
└── settings.json   — 构建设置（Markdown 扩展、日期格式）

content/{分类}/{文章}/  ← 每篇文章一个文件夹
├── index.html      — 生成的页面
├── index.md        — 原始 Markdown（带本地化图片路径）
└── 图片文件.jpg

archetypes/
└── archetype.html  — 全站 HTML 模板
```

---

## 写作技巧

- **换行**：单个换行 → `<br>`，双换行 → 新段落
- **分隔线**：`<!--sep-->` 强制换行但不分段
- **数学公式**：`$...$` 行内，`$$...$$` 块级
- **代码块**：标注语言以启用高亮
- **图片**：支持 `![alt](path)` 和 `![[path]]`（Obsidian 语法）
