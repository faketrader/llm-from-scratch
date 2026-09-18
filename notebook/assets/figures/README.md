# TikZ 架构图资产

Notebook 中的模型、模块、张量与系统组件架构图以 TikZ 作为唯一源文件，编译后的同名 SVG 作为 Notebook 的稳定显示制品。流程、状态机、生命周期与时序图继续使用 Mermaid。

每个图使用独立的 `standalone` 文档，并引入共享样式：

```tex
\def\pgfsysdriver{pgfsys-dvisvgm.def}
\documentclass[tikz,border=8pt]{standalone}
\usepackage{fontspec}
\usepackage{xeCJK}
\setmainfont{texgyretermes-regular.otf}
\setCJKmainfont{FandolHei-Regular.otf}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,calc,shapes.geometric,backgrounds}
\input{assets/figures/diagram_styles.tex}
\begin{document}
\begin{tikzpicture}[my picture]
  % diagram
\end{tikzpicture}
\end{document}
```

目录按 Notebook 文件名分组，例如 `assets/figures/30_transformer/transformer-overview.tex`。Notebook 引用同目录下的 `.svg`，并提供 `.tex` 源文件链接。不得直接编辑生成的 SVG。

编译全部图：

```bash
python scripts/render_tikz_diagrams.py --write --jobs 4
```

只检查 SVG 是否存在且不旧于源文件和共享样式：

```bash
python scripts/render_tikz_diagrams.py
```
