# 在线阅读

教材网站按主入口的五篇42章生成，包含前言、阅读说明、符号与数学约定、中英文术语索引，以及各章对应的504道习题与参考解析。正文、题答与图示读取仓库内已有 LaTeX 文件。

阅读器支持全书目录、章内目录、章节切换、跨章公式图表链接、全文搜索、字号调整、矢量图放大和解析展开。教材与习题 PDF 可直接下载。

## 构建与阅读

依赖 Node.js 24+、pnpm 12.4.2、make4ht（TeX4ht）及项目 PDF 构建所需的 TeX Live。图示导出使用 XeLaTeX 与 dvisvgm。

在仓库根目录执行：

```sh
make web
make serve-web
```

打开 `http://127.0.0.1:8765/`。网站交付目录为 `dist/web/`，生成清单位于 `dist/web/book-manifest.json`。MathJax、字体与代码高亮版本由 `web/pnpm-lock.yaml` 固定，阅读时从本站加载。

## 构建过程

教材和习题由 make4ht 分别转换到 `build/web-work/`，TypeScript 构建程序通过 DOM 读取 TeX4ht 生成的章节、题目、解析、图表和引用结构。`make web` 在公共图源准备完成后并行执行两册 PDF 构建与网页转换，待两条流程均成功后组装 `dist/web/`、复制 PDF 并完成校验。PDF 内部仍按教材、习题的依赖顺序构建。所有构建默认增量执行：PDF 由 latexmk 的依赖数据库判断是否重编译，网页转换按教材、习题及 TeX4ht 配置的内容指纹分别复用，前端供应商资源按锁文件复用。普通构建保留这些缓存；`make clean` 显式清理 `build/` 中的中间状态并保留 `dist/` 交付产物，`make clean -- --all` 同时清理两者。

`web/tex4ht/tex4ht.cfg` 配置 HTML 语义标签、脚注与 XeLaTeX 的 CJK Unicode 输出；`web/tex4ht/make4ht.mk4` 编排 LaTeX/Biber 编译。

网页转换命中内容指纹时直接复用 HTML；需要重新转换时，先使成功标记失效并清空对应册的转换目录，再完成多轮编译。这样，中断产生的不完整 AUX、XREF 等文件不会进入下一次编译，PDF 构建缓存不受影响。

## 代码组织

```text
web/
├── build.ts              # 构建入口，按顺序编排各阶段
├── check.ts              # 独立检查现有交付产物
├── serve.ts              # 本地静态服务器
├── build/                # Node.js 构建模块
│   ├── paths.ts          # 源码、缓存和交付路径
│   ├── types.ts          # 章节、习题与搜索条目的数据结构
│   ├── files.ts          # 进程、文件遍历与内容指纹
│   ├── conversion.ts     # make4ht 转换与增量缓存
│   ├── dom.ts            # DOM 基础操作与数学文本规范化
│   ├── textbook.ts       # 提取教材章节和附加内容
│   ├── workbook.ts       # 绑定习题与解析
│   ├── content.ts        # 规范化正文、图表和段落锚点
│   ├── references.ts     # 引文与跨章链接
│   ├── navigation.ts     # 全书和章内导航
│   ├── indexes.ts        # 搜索与术语索引
│   ├── render.ts         # 将内容填入页面模板
│   ├── version.ts        # 从书稿读取 PDF 下载版本
│   ├── assets.ts         # 浏览器资源、样式和供应商资源
│   └── validate.ts       # 页面结构、链接、锚点与搜索校验
├── templates/            # layout、home、chapter、extra HTML
├── client/               # 浏览器 ES 模块及 MathJax 配置
│   └── styles/           # 阅读布局、正文、交互、响应式、导航、代码和首页
└── tex4ht/               # TeX4ht 语义配置与 make4ht 编译流程
```

`convert.ts` 提前生成可缓存的 TeX4ht 转换结果；`build.ts` 复用转换结果，依次执行提取、引用绑定、渲染、资源发布与校验。构建模块通过 `types.ts` 共享数据结构；浏览器模块只依赖浏览器 API。首页、章节和附加页各自从公共布局生成。

样式按 `assets.ts` 中声明的顺序合并成一个 `styles.css`，保持层叠顺序。浏览器使用原生 ES 模块，构建时为入口及其导入加上内容版本号。发布文件名与页面地址由构建层统一生成。
网页下载的两册 PDF 使用 `book/preamble.tex` 中的书稿版本命名，例如 `textbook-0.1.0-20260924.pdf`；本地 `dist/textbook.pdf` 和 `dist/workbook.pdf` 保持固定文件名。

## 验证

```sh
pnpm --dir web typecheck # TypeScript 严格类型检查
pnpm --dir web check   # 检查 dist/web 中的现有页面
make web              # PDF、网页生成和产物校验
```

`make web` 在输出完成后检查页面主标题、重复 ID、模板占位符、本地文件与锚点、图片来源及搜索目标。外部网站的可达性由独立核查确认。浏览器交互变更还需检查首页搜索、章节导航、字号设置及图片查看。

## 内容与发布

- `web/build.ts` 编排 make4ht 并基于 DOM 生成静态页面；篇章顺序、编号、公式、图表、术语、习题和引用语义均由 LaTeX/make4ht 输出，构建程序不解析 LaTeX 正文。
- `templates/` 提供公共布局及首页、章节、附加页模板；`client/` 提供公式配置、阅读交互、搜索与图片查看；`client/styles/` 按页面职责维护样式。
- TikZ 图从章节或既有独立图源读取，使用 `pgfsys-dvisvgm` 驱动生成矢量 SVG。
- 配套习题沿用习题册的题答绑定及选修标记，习题中的教材对象引用定位到对应章节。
- 全文索引由正文、题目及解析生成；搜索命中可直接定位段落，命中解析时展开对应解析。
- 术语索引按英文排序，提供中文、英文、缩写与定义入口。
- GitHub Actions 部署时只发布 `dist/web/`。网站是静态产物，服务器负责提供文件。

网页转换与 Notebook 运行是独立流程。实验材料的运行按项目学习契约与授权范围执行。

## GitHub Pages

推送书稿或网页构建相关文件到 `main` 后，`.github/workflows/pages.yml` 在固定的 TeX Live 容器中执行 `make web`，检查所有页面、引用和资源，再部署到 https://faketrader.github.io/llm-from-scratch/ 。也可在 Actions 页面手动触发。Notebook 独立维护；发布只上传 `dist/web/`。
