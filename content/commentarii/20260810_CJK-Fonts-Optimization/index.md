参考：[网页中文字体加载速度优化 - 字体分包 | Hehehai @一块木头](https://www.hehehai.cn/posts/chinese-web-font-optimize)
优化策略：于本地使用npm包cn-font-split对字体文件进行分包，依据字符频率及Unicode区间生成woff2切片及result.css，使浏览器按需加载所需字体。