# web-to-markdown

网页转 Markdown 工具。抓取网页正文，转成干净的 Markdown，适合存文章、做笔记。

## 安装

```bash
pip install -r requirements.txt
```

## 用法

```bash
# 单个网页转 Markdown 并保存
python w2m.py "https://example.com/article" -o article.md

# 直接打印到终端
python w2m.py "https://example.com/article"

# 批量：从文件读取 URL 列表
python w2m.py --batch urls.txt --out-dir ./notes

# 保留图片链接、加标题头
python w2m.py URL -o out.md --with-title
```

## 参数

- `-o/--output`：输出文件
- `--batch`：URL 列表文件（每行一个）
- `--out-dir`：批量模式输出目录
- `--with-title`：在开头加一级标题
- `--timeout`：请求超时（默认 15 秒）

## 说明

使用 readability 提取正文，html2text 转 Markdown。请遵守目标网站规则，控制频率。