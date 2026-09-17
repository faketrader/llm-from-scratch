const $ = (selector) => document.querySelector(selector);

export function initFigures() {
  for (const figure of document.querySelectorAll("figure")) {
    const img = figure.querySelector("img");
    if (!img) continue;
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.setAttribute("aria-label", `放大图示：${img.alt}`);
    function openFigure() {
      $("#figure-large").src = img.src;
      $("#figure-large").alt = img.alt;
      $("#figure-caption").textContent =
        figure.querySelector("figcaption")?.textContent ?? img.alt;
      $("#figure-dialog").showModal();
    }
    img.addEventListener("click", openFigure);
    img.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openFigure();
      }
    });
  }
  $("#figure-close").addEventListener("click", () => $("#figure-dialog").close());
  for (const dialog of document.querySelectorAll("dialog"))
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        const rect = dialog.getBoundingClientRect();
        if (
          event.clientX < rect.left ||
          event.clientX > rect.right ||
          event.clientY < rect.top ||
          event.clientY > rect.bottom
        )
          dialog.close();
      }
    });
}
