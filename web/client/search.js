const $ = (selector) => document.querySelector(selector);

export function initSearch() {
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
}
