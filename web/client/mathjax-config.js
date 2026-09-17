window.MathJax = {
  loader: { paths: { "mathjax-newcm": "vendor/fonts" } },
  tex: {
    tags: "none",
    macros: {
      mat: ["\\boldsymbol{#1}", 1],
      vect: ["\\boldsymbol{#1}", 1],
      Real: "\\mathbb{R}",
      softmax: "\\operatorname{softmax}",
      argmin: "\\operatorname*{arg\\,min}",
      dif: "\\mathop{}\\!\\mathrm{d}",
      constpi: "\\mathrm{π}",
      conste: "\\mathrm{e}",
      consti: "\\mathrm{i}",
      le: "\\leqslant",
      leq: "\\leqslant",
      ge: "\\geqslant",
      geq: "\\geqslant",
      num: ["#1", 1],
      frac: [
        "\\genfrac{}{}{}{}{\\mspace{3mu}#1\\mspace{3mu}}{\\mspace{3mu}#2\\mspace{3mu}}",
        2,
      ],
    },
  },
  options: {
    enableMenu: true,
    enableExplorerHelp: false,
  },
  startup: {
    ready() {
      MathJax.startup.defaultReady();
      MathJax.startup.promise.then(
        () => (document.documentElement.dataset.math = "ready"),
      );
    },
  },
};
