参考：[网页中文字体加载速度优化 - 字体分包 | Hehehai @一块木头](https://www.hehehai.cn/posts/chinese-web-font-optimize)
优化策略：
1. 构建页面时，使用 fontTools + brotli 从完整字体文件生成单个子集，优先加载。
2. 使用npm包 cn-font-split 对字体文件进行分包，依据字符频率及Unicode区间生成woff2切片及result.css，作为回退。