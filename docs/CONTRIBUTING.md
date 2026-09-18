# 贡献指南

本指南面向参与教材、习题、实验与阅读网站维护的贡献者。学习入口见 [README](README.md)；项目协作与验收要求见 [AGENTS.md](AGENTS.md)，实验维护还需遵循 [notebook/AGENTS.md](notebook/AGENTS.md)。

## 贡献流程

1. 确定问题位置、修改范围和预期结果。纠错请提供推导、复现步骤或一手来源；新增主题先说明学习目标、知识前置与现有内容的关系。
2. 阅读相关文档和源码，执行 `git status --short` 与 `git diff` 确认已有改动，保留与本次任务无关的修改。
3. 在独立分支上完成范围清晰的修改，同步受影响的引用、学习索引和说明。提交前审阅差异，仅暂存本次贡献的文件或代码块。
4. 按下文验证要求检查，并在 Pull Request 中说明修改内容、证据来源、执行过的命令与结果，以及尚待验证的条件。

小范围文字纠错可直接提交 Pull Request。结构调整、共享宏或新增实验需说明对整书、单章编译和学习路线的影响。提交信息使用 Conventional Commits，如 `docs: clarify autoregressive generation`；Codex 协作提交附加 `Co-authored-by: Codex <codex@openai.com>`。

## 文件职责

| 位置 | 维护内容 |
|---|---|
| `book/textbook/textbook.tex` | 教材入口与篇章收录顺序 |
| `book/textbook/chapters/` | 可独立编译的教材章节 |
| `book/textbook/frontmatter/`、`backmatter/` | 封面、前言、阅读说明、符号约定、术语索引与封底 |
| `book/workbook/workbook.tex`、`chapters/` | 习题册入口、题目与参考解析 |
| `book/workbook/labs/`、`examples/` | 实验指导与配套实践代码 |
| `book/preamble.tex` | 本书的文档结构、元数据与资源声明 |
| `book/my-book.sty`、`my-*.sty` | 共享样式入口及数学、格式（含图表）和环境模块 |
| `book/references.bib` | 统一文献数据库 |
| `book/figures/theory/` | 书内 TikZ 图源、共享图样式与矢量 PDF |
| `notebook/` | 实验、数据、图源与配套脚本 |
| `web/` | 在线阅读器与网页构建工具 |
| `build/` | 构建输出 |

教材负责原理、推导、教学例题和系统关系；习题册负责题目、参考解析及实验指导，可引用教材并链接实验。教材与实验的映射维护在习题册和项目文档中。源文件名前缀用于稳定定位，正式章号由教材入口的收录顺序生成。

## 内容与排版维护

教材章节沿用 `subfiles` 结构，共用主文件导言区，使用 `\bookchapter{标题}{ch:标签}` 声明章节，结尾调用 `\chapterreferences`。新增章节时更新主入口及相关规划与实践索引。资源使用相对路径和 `\subfix`，保持整书与独立章节均可定位。

跨章内容使用 `\bookxref` 或 `\bookxrefshort`；图、表、公式和算法通过语义标签引用，编号由构建生成。跨文件引用应提供独立编译时可理解的降级文本。

习题文件与教材同主题文件名一致，使用 `\workbookchapter{标题}`、`exercises` 列表中的 `exercise` 环境，选修题在环境开头调用 `\optional`。参考解析放在紧接题目的 `solution` 环境中，题目编号、题答绑定、双向跳转及书后解析分组由样式生成。

首次定义术语使用 `\term{中文规范名}{English Name}{缩写}`，后续直接使用中文名称或缩写；论证后的短结论使用 `\keyconcept`，一般语气强调使用 `\emph`。新增术语须在 `book/textbook/backmatter/term-index-keys.tex` 补充中文拼音排序键，ü 写作 v，多音字按词义确定。latexmk 自动调用 MakeIndex，教材书末生成中英文索引。

公式明确前提、符号和张量形状；分式使用 `\frac`，需要展示式大小时使用 `\dfrac`。数学语义命令集中在 `book/my-math.sty`，数值与单位使用 siunitx。表格使用 booktabs，并提供表题和语义标签；解释性短表使用 tabularx，紧凑数值短表可使用 tabular，跨页表使用 longtable。

字体沿用 ctex 平台默认配置，西文与数学保留 TeX 默认字体。共享样式集中管理依赖与排版；复杂宏新增或实质重构时优先使用成熟的 LaTeX3 接口，保持 XeLaTeX 与 LuaLaTeX 兼容。书籍采用双面排版，篇从右页起排，章换页，补白页保持空白，封底位于最后偶数页。

书内图示使用 TikZ，保留可维护的 `.tex` 与矢量 PDF。执行以下命令生成图示：

```sh
make figure FIGURE=revision-ch08-architecture
make figures
```

`make figure` 独立编译指定的 standalone TikZ 图，文件名参数不带目录和扩展名；输出同时写入 `build/figures/<文件名>/` 和图源目录，适合修改后单独核对。`make figures` 只重建教材与习题当前引用且需要更新的 TikZ 图。

数据曲线可使用 PGFPlots，输入来自真实计算；图内字体与数学表达遵循正文规范。图示应解释机制、结构或信息流，并说明可能的误读边界。

## 文献与实验维护

方法、模型规格、API 行为和性能结论优先核对论文、官方文档或固定版本源码，记录作者或机构、发布日期、规范链接、访问日期及适用条件。软件引用先检查 CITATION.cff、推荐引用或 DOI；具体实现绑定 release/tag 或 commit。厂商报告的性能与收益注明来源、设备和测试条件，理论结论、实验观察与生产验证分别陈述。

文献通过 Zotero 本地 API 管理。每次使用先确认服务连通；创建前按 DOI、arXiv ID、标题与作者检索并核对候选元数据，已有条目直接复用。随后按条目维护 `book/references.bib`，保留已使用的引用键。整书文献位于书末，独立章节列本章引用。授权与密钥处理遵循 [AGENTS.md](AGENTS.md) 的 Zotero 规则；凭据保存在被 Git 忽略、权限为 600 的本地 `.env`，日志和提交保持无敏感信息。

实验采用学习契约、直觉与输入输出契约、最小原理实现、证据验证、生产库迁移、生产边界的六段结构，具体要求见 [notebook/AGENTS.md](notebook/AGENTS.md)。每个实验明确版本、资源与资产前置，跨实验传递版本化文件和 Manifest，保持独立的数据与定义依赖。关键数值在首次定义处解释作用、单位、选择依据与调整影响，完整选择方法见[数值与超参数阅读手册](notebook/HYPERPARAMETERS.md)。

实验架构图使用 TikZ 并导出自包含 SVG，过程与状态图使用 Mermaid，测量图来自实际计算。实验图源按实验目录的构建脚本维护。云盘与仓库之间的同步逐文件比较，保留两侧有效修改。训练产物、缓存、密钥与机器私有配置留在本地。

## 构建与验证

PDF 构建依赖 GNU Make 和 TeX Live 2026 / MacTeX，以及 XeLaTeX、latexmk、ctex、subfiles、xr-hyper、biblatex、Biber 和 MakeIndex，不依赖 Python。默认引擎为 XeLaTeX，配置位于 `.latexmkrc`。在仓库根目录按修改范围执行：

```sh
make chapter CHAPTER=14-optimization-generalization
make textbook
make workbook
make books
make chapters
```

`make workbook` 先构建教材，再由 `xr-hyper` 直接读取教材 AUX 中的编号；`make chapter` 先更新教材 AUX，再从中读取当前章号、跨章标题和链接；各章是独立 Make 目标，`make chapters` 按稳定顺序完成全量构建。教材、习题和单章的编译状态分别位于 `build/textbook/`、`build/workbook/`、`build/chapters/<章节名>/`，两册交付 PDF 位于 `dist/`。

| 修改范围 | 必要验证 |
|---|---|
| README、贡献指南等入口文档 | 差异、链接目标与命令一致性检查 |
| 普通教材内容 | 编译受影响章节，检查日志 |
| 习题或实验指导 | 构建习题册，检查题答绑定与教材引用相关日志 |
| 共享排版、篇章顺序或 PDF 构建 | 编译两册及所有独立章节，检查日志 |
| 网页转换或阅读器 | 执行 `make web` 的生成与检查流程；交互改动另做浏览器验证 |
| Notebook | 默认检查文件结构、代码语法、链接和资产引用；明确请求运行后按授权范围执行 |

PDF 检查编译错误、缺字和未解析引用，按项目约定跳过页面渲染。Notebook 静态检查与实际运行分别报告；训练、推理和联网下载按明确的运行范围执行。验证记录注明命令、结果与适用条件。

需要切换引擎时使用 `latexmk -lualatex book/textbook/textbook.tex`，入口可替换为习题或独立章节；切换后重新构建更新分页和引用。排版诊断可在导言区显式加载 `\usepackage{lua-visual-debug}` 并使用 LuaLaTeX。

构建默认生成 PDF 同目录下的 `.synctex.gz`。保留 PDF、同步文件和原源码路径后，支持 SyncTeX 的查看器可进行 PDF 与源码跳转，快捷键由查看器配置决定。

## 网站发布与构建清理

网站依赖 make4ht（TeX4ht）、Node.js 24+/pnpm 12.4.2、TeX Live 和 dvisvgm。执行：

```sh
make web
make serve-web
```

访问 `http://127.0.0.1:8765/`，网站交付产物位于 `dist/web/`，中间状态位于 `build/web-work/` 和 `build/web-cache/`。网站沿用 LaTeX 正文、编号与题答，构建流程同时检查页面、引用及资源。阅读器与发布细节见 [web/README.md](web/README.md)。

`.github/workflows/pages.yml` 在 `main` 的相关文件更新后构建并部署 GitHub Pages，也支持手动触发；部署目录为 `dist/web/`。

`make release` 构建两册并更新 `dist/` 中的交付 PDF；`make clean` 清理 `build/` 中的编译状态并保留交付产物，`make clean -- --all` 同时清理 `build/` 与 `dist/`。运行清理命令前确认所需日志和诊断记录已保存。

算法使用 algorithm 环境提供章内编号；输入、输出和状态契约分别使用 `\AlgoInput{}`、`\AlgoOutput{}` 和 `\AlgoState{}`，不得手写加粗标签；计算过程中的循环和分支使用 algorithmic 与 algpseudocode 命令，伪代码块保留英文，算法标题和正文解释使用中文；工程流程保留完整步骤与停止条件。代码块使用 minted，标明语言并保留原文。提示框使用 assumption（前提）、note（说明）和 warning（注意），标题写明具体对象与条件。
