# 在线阅读

教材网站按主入口的五篇42章生成，包含前言、阅读说明、符号与数学约定、中英文术语索引，以及各章对应的504道习题与参考解析。正文、题答与图示读取仓库内已有 LaTeX 文件。

阅读器支持全书目录、章内目录、章节切换、跨章公式图表链接、全文搜索、字号调整、矢量图放大和解析展开。教材与习题 PDF 可直接下载。

## 构建与阅读

依赖 Python 3、Pandoc、Node.js/npm，以及项目 PDF 构建所需的 TeX Live。图示导出使用 XeLaTeX 与 dvisvgm。

在仓库根目录执行：

```sh
make web
make serve-web
```

打开 `http://127.0.0.1:8765/`。网站输出目录为 `build/web/`，生成清单位于 `build/web-work/book-manifest.json`。MathJax 与字体版本由 `web/package-lock.json` 固定，阅读时从本站加载。

## 内容与发布

- `scripts/build_web_book.py` 读取教材入口决定篇章顺序，使用原书 LaTeX 编号生成公式与引用，经 Pandoc 解析正文和文献；未适配的原始 LaTeX 节点、未知引用、公式及图示编号差异会终止构建。
- `reader.html`、`reader.css`、`reader.js` 提供阅读布局、样式与浏览器交互。
- TikZ 图从章节或既有独立图源读取，使用 `pgfsys-dvisvgm` 驱动生成矢量 SVG；中间图源和编译记录位于 `build/web-work/`。
- 配套习题沿用习题册的题答绑定及选修标记，习题中的教材对象引用定位到对应章节。
- 全文索引由正文、题目及解析生成；搜索命中可直接定位段落，命中解析时展开对应解析。
- 术语索引按英文排序，提供中文、英文、缩写与定义入口。
- 部署时只发布 `build/web/`。网站是静态产物，服务器负责提供文件。
- `make release` 清理 PDF 构建目录中的辅助文件；网页及其构建记录使用独立目录。

网页转换与 Notebook 运行是独立流程。实验材料的运行按项目学习契约与授权范围执行。

## GitHub Pages

推送书稿或网页构建相关文件到 `main` 后，`.github/workflows/pages.yml` 在固定的 TeX Live 容器中执行 `make web`，检查所有页面、引用和资源，再部署到 https://faketrader.github.io/llm-from-scratch/ 。也可在 Actions 页面手动触发。Notebook 独立维护；发布只上传 `build/web/`。
