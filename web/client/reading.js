const $ = (selector) => document.querySelector(selector);

export function initReading() {
  const sidebar = $("#sidebar");
  const menuToggle = $("#menu-toggle");
  if (sidebar && menuToggle) {
    menuToggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(open));
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
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  }
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
    const status = $("#reading-status");
    if (status) status.textContent = `已读 ${percentage}%`;
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
    if ($("#font-smaller")) $("#font-smaller").disabled = size === 15;
    if ($("#font-larger")) $("#font-larger").disabled = size === 21;
  }
  setSize(size);
  $("#font-smaller")?.addEventListener("click", () => setSize(size - 1));
  $("#font-larger")?.addEventListener("click", () => setSize(size + 1));
}
