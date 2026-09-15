# LLM from Scratch: Zero to Hero

中文大语言模型教材与配套实践。本项目的三类学习材料统一称为教材（textbook，缩写 `tb`）、习题（workbook，缩写 `wb`）和实验（notebook，缩写 `nb`）；项目命名不使用 `main` 指代教材。教材解释原理、推导和工程关系，实验提供从零实现、证据验证与生产库迁移；三者按主题多对多关联，不要求编号或章节一一对应。

“从零”指从基本运算构建大模型核心机制；读者仍需 Python、线性代数、概率与基础微积分知识。全书为五篇42章，24个实验独立维护。

本项目交付两册 PDF：教材入口 `book/textbook/textbook.tex`，输出 `build/textbook/textbook.pdf`，只保留理论、推导、教学例题和系统分析；习题入口 `book/workbook/workbook.tex`，输出 `build/workbook/workbook.pdf`，书名为《习题解析与实验指导》，集中42章的504道习题、504份参考解析及24个实验指导。教材不引用习题或实验，习题可以引用教材并定位实验。两册在外侧页边用危险弯道图标（manfnt）标识选修。两册与独立章节通过统一构建命令生成。

篇章规划见 [LFS 全书规划](docs/lfs-plan.md) 与 [XMind 思维导图](docs/llm-from-scratch.xmind)，参考资料见 [references/](references/README.md)。

## 阅读路线

先建立模型输入、Transformer 前向计算、自回归生成及基本评估与安全的共同基础，再按目标选择**应用智能体系统、模型训练方法、训练推理系统**。Harness 位于应用智能体系统的深入专题；系统方向分别提供训练系统和推理服务分支。各方向按需补齐专项理论，并选读多模态等专题。

正文按五篇42章编排：语言模型理论基础、应用智能体系统、模型训练方法、训练推理系统、模型架构拓展。各方向的前置、阅读顺序和学习终点见[全书阅读路线](docs/lfs-plan.md#阅读路线共同基础与三条方向)。实践仍须满足对应 Notebook 的实际学习契约和运行前置。

## 编译

安装 TeX Live 2026 / MacTeX（含 XeLaTeX、LuaLaTeX、latexmk、ctex、subfiles、biblatex、Biber），项目默认使用 XeLaTeX；共享样式兼容 XeLaTeX 和 LuaLaTeX。构建辅助脚本使用 Python 3 标准库。构建不需要 Python 模型库、GPU、联网下载或 shell escape。

正式构建采用常规排版输出。需要可视化排版诊断时，在导言区显式加载 `\usepackage{lua-visual-debug}` 并使用 LuaLaTeX；该包在 PDF 中标注盒子、弹性间距、字距和断行惩罚。

字体使用 ctex 的平台默认配置，不指定 `fontset`，不手工设置字体族；西文与数学保留 TeX 默认字体。不同操作系统的默认中文字体可能不同，需具备 ctex 在对应平台所需的字体。正文与图表遵循同一配置，使用 ctex 提供的字体命令。

正文保持 ctexbook 的默认行距和段距，仅在行内分式使相邻行净空过小时增加局部行间距；复杂分式使用独立公式。

在仓库根目录执行：

```sh
make check-references # 检查是否存在手填引用编号
make textbook         # 教材
make workbook         # 习题（先核对教材编号）
make books            # 两册
make release    # 构建两册并仅保留PDF与SyncTeX
make chapter CHAPTER=14-optimization-generalization
make chapters
```

教材输出 `build/textbook/textbook.pdf`，习题输出 `build/workbook/workbook.pdf`；独立章节输出 `build/chapters/<章节名>/<章节名>.pdf`。`make release` 在验证构建后清除 PDF 构建目录中的辅助文件，仅保留 PDF 与 SyncTeX；`make clean` 清理构建目录和可再生成的跨章、跨册编号缓存。

## 在线阅读

网页与 PDF 共用现有 LaTeX 正文。运行 `make web` 生成全书网站，输出位于 `build/web/`；运行 `make serve-web` 后访问 `http://127.0.0.1:8765/`。网站提供篇章目录、公式图表链接、术语索引、全书搜索和配套习题解析。在线地址为 https://faketrader.github.io/llm-from-scratch/ ，推送书稿或构建文件到 `main` 后由 GitHub Actions 自动构建、检查并发布静态输出目录。构建依赖与发布说明见 [在线阅读](web/README.md)。

## PDF 与源码跳转

构建默认启用 SyncTeX（`-synctex=1`），在 PDF 同目录生成同名 `.synctex.gz`：教材为 `build/textbook/textbook.synctex.gz`，独立章节位于各自输出目录。保留 PDF、同步文件及原项目源码路径，支持 SyncTeX 的查看器才能将 PDF 位置映射回实际的章节或主题 `.tex`。正向与反向跳转的快捷键、编辑器调用方式由查看器配置决定；普通 PDF 预览器不一定支持。

需要使用 LuaLaTeX 时，可运行 `latexmk -lualatex book/textbook/textbook.tex`，或将入口替换为习题、独立章节；输出目录和 SyncTeX 规则保持一致。切换引擎后重新构建以更新分页和引用。

## 目录与写作

```text
book/
  textbook/
    textbook.tex           教材入口、分篇、目录
    frontmatter/           封面、前言与符号约定
    backmatter/            教材术语索引与封底
    chapters/              42 个可独立编译章节
  workbook/
    workbook.tex           《习题解析与实验指导》入口
    chapters/              同章习题与参考解析，解析集中排在书后
    labs/                  24份实验指导
    examples/              配套实践代码
  preamble.tex             共用元数据、文献和数学配置入口
  mybook.sty               可复用版式、宏包依赖和书籍命令
  mymath.sty               数学语义命令
  termindex.sty            术语索引配置
  references.bib           统一文献数据库
  figures/theory/          结构图源文件、样式与矢量 PDF
notebook/                 实践 Notebook、数据、图源和配套脚本
docs/practice-map.md      章节—实验索引
AGENTS.md                  项目协作与验收规范
.latexmkrc                 XeLaTeX 默认构建配置
Makefile                   统一命令入口
```

习题册每章在 `book/workbook/chapters/` 的同主题命名文件内维护题目与参考解析，文件名与教材章节一致，例如 `11-introduction.tex`。章节以 `\workbookchapter{标题}` 声明；每道题使用无参数的 `\exerciseitem`，选修题紧随其后调用 `\optional`；对应解析直接放入紧接题目的 `workbookanswers` 环境。源码不手填章序、题序、题目标签、解析标签、`\answerchapter` 或 `\answeritem`。章节与题目编号、解析分组及题答双向跳转均由样式按收录顺序自动生成并绑定，解析在书后的参考解析部分统一输出。

新增章节采用现有章节的 `subfiles` 结构，调用 `\bookchapter{标题}{ch:标签}`，结尾调用 `\chapterreferences`，并按目标顺序加入主入口及更新[实践索引](docs/practice-map.md)。章号由主入口中的收录顺序自动生成，禁止在章节声明或交叉引用中手填。新增图片使用相对路径和 `\subfix`，保持整书、单章两种构建均可定位资源。跨章内容使用 `\bookxref` 或 `\bookxrefshort`；图、表、公式、算法和实验使用标签引用，不直接写最终显示编号。跨文件标签应提供独立编译时的明确降级文本，不能依赖其他章节的辅助文件。

写作、术语、伪代码与强调格式遵循[教材写作与排版规范](docs/editorial-standard.md)。

关键术语首次定义使用 `\term{中文规范名}{English Name}{缩写}`：中文规范名加粗，英文全称与缩写保持常规字重；后文不重复强调。短结论使用 `\keyconcept`，一般语气强调使用 `\emph`。

## 排版与文献约定

教材书末设置两份术语索引：中文术语索引按拼音排序，英文术语索引按英文名称的字母顺序排序。索引只列术语及其页码，收录正文 `\term` 标记在每章的首次位置，点击页码可直接跳到对应术语；不对全文所有同词出现位置做机械索引。`latexmk` 自动调用 MakeIndex 并更新页码，无需手动运行索引命令。新增术语时在 `book/textbook/backmatter/term-index-keys.tex` 补充中文拼音排序键（ü 写作 v，多音字按词义确定）；缺少排序键会报错。索引仅在教材生成，习题和独立章节不另列索引。

`mybook.sty` 使用标准宏包声明管理依赖、页面样式和书籍命令；`preamble.tex` 加载样式并声明本书标题、页眉、PDF 元数据、文献库及数学命令。`textbook.tex` 只负责文档类和内容组织。整书与独立章节共用同一套配置。

整书使用 `twoside,openany`：封面、前言、目录和各篇从右页开始，各章只换页、不补白到右页；自动补出的空白页无页眉页脚，封底位于最后一个偶数页。封面与封底无印刷页码，前言和目录使用小写罗马页码，正文从 1 开始。内侧页边距 30 mm、外侧 24 mm，页眉页码镜像排列；双面打印采用长边翻转。本文件是顺序阅读与双面打印 PDF，不包含印厂拼版、书脊或出血设置。

[绪论](book/textbook/chapters/11-introduction.tex)位于“语言模型理论基础”篇开头，基础机制按文本表示、注意力、Transformer 整体结构、位置表示、自回归生成展开，评估与安全位于篇末。应用篇从上下文、检索与 RAG 进入领域应用及智能体运行系统；训练篇涵盖优化、数据、微调、预训练、人类反馈学习；系统篇分别展开训练与推理；模型架构与多模态篇按任务选读。章号按主入口顺序连续生成，PDF 书签显示编号。

作者在 `preamble.tex` 的 `\bookauthor` 中统一维护，封面、LaTeX 作者字段与 PDF 元数据共用该署名。

数学分式统一使用 `\frac{分子}{分母}`，需要展示式大小时使用 `\dfrac`，不以 `/` 排写；教材、习题与图内公式遵循同一约定。

数学配置集中在 `book/mymath.sty`：`\dif x` 为微分，`\Real` 为实数集，`\softmax` 与 `\argmin` 为算子；按正文需要新增语义命令，不全局使用展示式行内公式。数值与单位使用 `siunitx`，例如 `\num{10000}`、`\qty{250}{\milli\second}`；数值表格按需使用 `S` 列。表格统一使用 `booktabs`，表体字号由共享样式控制；章节正式表格提供表题和语义标签。解释性短表使用 `tabularx`，紧凑的纯数值短表可使用 `tabular`，真正需要跨页的理论与接口表使用 `longtable`。长接口名支持换行，目录列到节级，避免细分主题淹没主线。

文献使用 Zotero 管理，并在 `book/references.bib` 中维护书稿引用及一致的引用键。新增方法与规格须核实一手来源并记录适用版本。整书文献集中在书末，独立章节列本章引用，各篇不重复列文献；收录或静态引用解析不代表实验验证。

书籍写作参考资料保存在 [references/](references/README.md)，含用户提供的两份参考书、来源说明和 SHA-256 校验记录。

## 实践材料

[实践路线](notebook/README.md)按共同基础、三条方向与跨方向专题组织，[主题关联](docs/practice-map.md)给出与书籍的联系。打开 Notebook 时以 `notebook/` 作为工作目录；不得依赖其他 Notebook 的内存状态。模型和数据依赖按各 Notebook 的说明准备。

实验及配套图片、TikZ 源码、Tokenizer 数据和脚本通过本仓库维护。与云盘目录合并时逐文件比较，保留各自有效修改。

Notebook 默认仅静态检查，不自动运行训练、推理或下载。导入并不代表其运行环境、依赖和实验结果已经重新验证。PDF 生成按项目约定跳过页面渲染检查，仍检查编译错误、缺字与未解析引用。

框架实践集中在习题的[微调与后训练实验](book/workbook/labs/08-42_peft.tex)、[分布式训练实验](book/workbook/labs/17-A40_training_optimization.tex)和[推理部署实验](book/workbook/labs/10-60_inference_deployment.tex)。覆盖Transformers、PEFT、TRL、LLaMA-Factory、Axolotl、DeepSpeed、FSDP2、Megatron-LM、vLLM、SGLang及TensorRT-LLM；教材的[参数高效微调](book/textbook/chapters/42-parameter-efficient-finetuning.tex)、[分布式训练](book/textbook/chapters/62-distributed-training.tex)和[模型服务架构](book/textbook/chapters/64-serving-architecture.tex)分别解释对应框架职责与技术取舍。配套训练入口为 `book/workbook/examples/train_adapter.py`，使用本地模型与数据，运行要求见实验；本次框架实践尚未执行。

## 理论覆盖与图表维护

正文覆盖实验涉及的理论，按概念依赖组织。公式说明前提、符号与形状，图示解释结构与信息流；教材与实验的主题关联维护在[实践索引](docs/practice-map.md)中。

42章正文直接维护于 `book/textbook/chapters/`。

正文采用与论证相关的结构图，保留 TikZ 源文件与矢量 PDF。历史导入图源继续保留，但不按导入数量评价正文覆盖。新增图示包括反向传播、RAG 工具执行与 KV 增量解码。实验测量图留在 Notebook，并由真实计算产生。

书内新增或重绘图示统一使用 TikZ，编辑 `book/figures/theory/` 下的 `.tex`，执行 `python3 scripts/build_theory_figures.py --kind tikz` 生成矢量 PDF，字体沿用 ctex 默认配置。数据曲线可使用基于 TikZ 的 PGFPlots，输入须来自真实计算。历史 `.mmd` 图源与对应构建选项暂时保留，不作为后续绘图方式；本次记录约定不批量转换既有图示。图表构建不执行 Notebook。
