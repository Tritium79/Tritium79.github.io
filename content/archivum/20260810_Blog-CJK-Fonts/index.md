参考：[网页中文字体加载速度优化 - 字体分包 | Hehehai @一块木头](https://www.hehehai.cn/posts/chinese-web-font-optimize)
优化策略：
1. 构建页面时，使用pip包`fontTools`与`brotli`自动从完整字体文件生成单字子集`subset-lxgw-light.woff2`与`subset-lxgw-medium.woff2`，优先加载，并preload。
2. 使用npm包`cn-font-split`对字体文件进行分包，依据字符频率及Unicode区间生成`woff2`切片及`result.css`，作为回退。