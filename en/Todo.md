# EN 站点待办清单

> 中文站的对应结构为本站的翻译母本。勾选项表示已完成。

---

## 一、内容补齐（翻译文章）

en 站目前每分类仅 1 篇样张，中文站已有 24 篇。需按下列映射补齐（文件夹沿用中文的 `{YYYYMMDD}_{Slug}`，标题/正文译成英文）。

### Sylvae（中文 7 篇 / en 现有 1 篇）

- [x] 20260508_Blog-Init → Init（已完成）
- [ ] 20260508_Cat-Record → 偶遇小猫（建议：Stray Cat）
- [ ] 20260510_Daily-Photograph-1 → 生活日常（一）（建议：Daily Photograph (1)）
- [ ] 20260518_iPhone-Air → iPhone Air
- [ ] 20260620_iPad-mini → iPad mini (A17 Pro)
- [ ] 20260629_Daily-Photograph-2 → 生活日常（二）（建议：Daily Photograph (2)）
- [ ] 20260828_Blog-Domain → 博客域名（建议：Blog Domain）

### Scripta（中文 7 篇 / en 现有 1 篇）

- [x] 20260816_Latina → Latina（已完成）
- [ ] 20260515_Software-Config → 软件记录（建议：Software Records）
- [ ] 20260810_Blog-CJK-Fonts → [博客建设]CJK字体加载优化（建议：[Blog] CJK Font Loading）
- [ ] 20260810_Blog-Design → [博客建设]网页设计（建议：[Blog] Design）
- [ ] 20260810_Blog-Dev → [博客建设]网站运行维护（建议：[Blog] Development / Ops）
- [ ] 20260812_Blog-Gamut → [博客建设]色彩管理（建议：[Blog] Color Management）
- [ ] 20260812_Blog-Photos → [博客建设]图片处理（建议：[Blog] Image Processing）

### Transcripta（中文 7 篇 / en 现有 1 篇）

- [x] 20260508_OA-Introduction → 已建（Sci-Fi Stories / Orion's Arm 简介；与中文 `OA-Introduction-Translation` 的关系待确认，若为同一篇可改用统一 slug）
- [ ] 20260612_Misere → 「论大学生的贫乏」（建议：On the Poverty of University Students）
- [ ] 20260825_OA-GAIA-and-the-Great-Expulsion → [译稿]地球、GAIA与大驱逐
- [ ] 20260825_OA-Nuclear-Pasta-Life → [译稿]中子星核意面生物
- [ ] 20260825_OA-The-Tranquility-Calendar → [译稿]静海历
- [ ] 20260831_OA-History-of-Luna-Civilization → [译稿]月球文明的历史
- [ ] 20260905_OA-Toposophy → [译稿]拓扑智识位阶、飞升奇点、心智类别

### Archivum（中文 3 篇 / en 现有 1 篇）

- [x] 20260509_Format-Date → Date Format（已完成）
- [ ] 20260515_Latex-Format-Test → LaTeX Format Test
- [ ] 20260515_Markdown-HTML-Format-Test → Markdown & HTML Format Test

> 注意：en 文章日期使用纯西历（如 `8 May. 2026`），不含中文站的干支后缀。

---

## 二、页面 / 汇总页同步

- [ ] 每补一篇即更新对应 `pages/{cat}.html` 的 `<ol class="link-list">`（标题 + `article-date`）
- [ ] `page-desc` 文案复查（当前：Essays. / Records. / Transcript. / Archive. / Link exchange. / About this Blog and me.）
- [ ] `en/content/` 若有配图，确认图片随文章本地化、相对路径正确

---

## 三、多语言入口与互链

- [ ] 增加语言切换入口（中文站 ↔ EN ↔ LA，参考 tei-ku：`/`、`/en/`、`/la/`）
- [ ] 根中文站页脚/导航加入指向 `/en/`、`/la/` 的链接（当前中文站无任何外链到 en）
- [ ] 确认 en footer 域名路径（现为 `https://tritium79.com/en`）与中文站（`https://tritium79.com/`）区分正确

---

## 四、la（拉丁文站）

- [ ] 待搭建：`/la/` 目前为空。参考 tei-ku 目录隔离方案：`la/index.html`、`la/pages/`、`la/content/`
- [ ] 决定 la 是否复用 en 的 Cormorant Garamond 字重/子集，或引入拉丁专用字体
- [ ] 决定 la 内容范围（全部翻译 or 精选）
- [ ] en/la 语言切换加入 la 项

---

## 五、工程化 / 构建接入（可选，长期）

- [ ] 当前 en 站为纯手工维护，未接入 `build.py` 数据驱动（`data/`、`archetypes/` 变量渲染、字体子集、模板一致性检查）
- [ ] 若接入：评估 `data/` 增加语言维度（每语言一套 config/categories）与 `build.py` 增加 `--lang` 的改造范围
- [ ] 决定 `en/style.css` 与中文 `style.css` 的同步策略（当前 en 剔除了 lxgw 中文字体导入、改用 Cormorant Garamond 正文栈，放在 en/style.css 尾部覆盖）
- [ ] README-Full.md / AGENTS.md 需补记多语言目录结构（en/、la/ 顶层目录）

---

## 六、部署与 SEO（可选）

- [ ] `robots.txt`：确认是否允许爬取 `/en/`、`/la/`
- [ ] `sitemap.xml` 与 `hreflang`（`<link rel="alternate" hreflang>`）— 若在意 SEO 再补
- [ ] CNAME / 域名路由验证 `/en`、`/la` 子路径可访问（静态站通常天然可用）
- [ ] en 各页 KaTeX：目前 4 篇均无数学；若后续译文含公式，需按中文站逻辑注入 KaTeX
