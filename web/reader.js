const $ = (selector) => document.querySelector(selector);
const sidebar = $("#sidebar");
$("#menu-toggle").addEventListener("click", () => {
  const open = sidebar.classList.toggle("open");
  $("#menu-toggle").setAttribute("aria-expanded", String(open));
  if (open) showCurrentChapter();
});
function showCurrentChapter() {
  const current = sidebar.querySelector('a[aria-current="page"]');
  if (current && sidebar.clientHeight) {
    sidebar.scrollTop += current.getBoundingClientRect().top - sidebar.getBoundingClientRect().top - 140;
  }
}
requestAnimationFrame(showCurrentChapter);
sidebar.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    sidebar.classList.remove("open");
    $("#menu-toggle").setAttribute("aria-expanded", "false");
  }
});
const links = [...document.querySelectorAll('nav[aria-label="本章目录"] a')];
const headings = links.map((link) =>
  document.getElementById(decodeURIComponent(link.hash.slice(1))),
);
function updateReading() {
  const total = document.documentElement.scrollHeight - innerHeight;
  const percentage = Math.min(
    100,
    Math.max(0, Math.round((scrollY / Math.max(1, total)) * 100)),
  );
  $("#progress-fill").style.width = `${percentage}%`;
  $("#reading-status").textContent = `已读 ${percentage}%`;
  let active = 0;
  headings.forEach((heading, index) => {
    if (heading && heading.getBoundingClientRect().top < 170) active = index;
  });
  links.forEach((link, index) => {
    link.classList.toggle("active", index === active);
    if (index === active) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  });
}
let scheduled = false;
addEventListener(
  "scroll",
  () => {
    if (!scheduled)
      requestAnimationFrame(() => {
        updateReading();
        scheduled = false;
      });
    scheduled = true;
  },
  { passive: true },
);
addEventListener("resize", updateReading);
updateReading();
let size = 17;
try {
  size = Number(localStorage.getItem("lfs-font-size")) || 17;
} catch {}
function setSize(value) {
  size = Math.max(15, Math.min(21, value));
  document.documentElement.style.setProperty("--body-size", `${size}px`);
  try {
    localStorage.setItem("lfs-font-size", String(size));
  } catch {}
  $("#font-smaller").disabled = size === 15;
  $("#font-larger").disabled = size === 21;
}
setSize(size);
$("#font-smaller").addEventListener("click", () => setSize(size - 1));
$("#font-larger").addEventListener("click", () => setSize(size + 1));
const searchDialog = $("#search-dialog");
function openSearch() {
  searchDialog.showModal();
  $("#search-input").focus();
}
$("#search-open").addEventListener("click", openSearch);
$("#search-close").addEventListener("click", () => searchDialog.close());
addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    if (!searchDialog.open) openSearch();
  }
});
let searchIndex = null;
let searchLoading = null;
let searchGeneration = 0;
async function loadSearch() {
  if (searchIndex) return searchIndex;
  if (!searchLoading)
    searchLoading = fetch("search-index.json")
      .then((response) => {
        if (!response.ok) throw new Error("Search index unavailable");
        return response.json();
      })
      .then((data) => {
        searchIndex = data;
        return data;
      })
      .catch((error) => {
        searchLoading = null;
        throw error;
      });
  return searchLoading;
}
$("#search-input").addEventListener("input", async (event) => {
  const generation = ++searchGeneration;
  const query = event.target.value.trim().toLocaleLowerCase();
  $("#search-results").replaceChildren();
  if (!query) {
    $("#search-count").textContent = "搜索全书正文、习题与解析";
    return;
  }
  $("#search-count").textContent = "正在搜索…";
  try {
    const index = await loadSearch();
    if (generation !== searchGeneration) return;
    const results = index.filter((item) =>
      item.text.toLocaleLowerCase().includes(query),
    );
    $("#search-count").textContent =
      `找到 ${results.length} 处匹配${results.length > 50 ? "，显示前 50 处" : ""}`;
    $("#search-results").replaceChildren(
      ...results.slice(0, 50).map((item) => {
        const link = document.createElement("a");
        link.href = item.url;
        const title = document.createElement("span");
        title.className = "search-result-title";
        title.textContent = item.title;
        const position = item.text.toLocaleLowerCase().indexOf(query);
        const start = Math.max(0, position - 35);
        const snippet = document.createElement("span");
        snippet.textContent =
          (start ? "…" : "") +
          item.text.slice(start, start + 155) +
          (item.text.length > start + 155 ? "…" : "");
        link.append(title, snippet);
        link.addEventListener("click", () => searchDialog.close());
        return link;
      }),
    );
  } catch {
    if (generation === searchGeneration)
      $("#search-count").textContent = "搜索加载失败，请刷新后重试。";
  }
});
// Search destinations inside a reference answer should reveal that answer.
function revealHash() {
  const target = document.getElementById(
    decodeURIComponent(location.hash.slice(1)),
  );
  const details = target?.closest("details");
  if (details) {
    details.open = true;
    target.scrollIntoView();
  }
}
addEventListener("hashchange", revealHash);
revealHash();
for (const figure of document.querySelectorAll("figure")) {
  const img = figure.querySelector("img");
  img.tabIndex = 0;
  img.setAttribute("role", "button");
  img.setAttribute("aria-label", `放大图示：${img.alt}`);
  function openFigure() {
    $("#figure-large").src = img.src;
    $("#figure-large").alt = img.alt;
    $("#figure-caption").textContent =
      figure.querySelector("figcaption").textContent;
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
