import type { Chapter } from "./types.ts";
import { EXTRA_PAGES, TERMS_PAGE } from "./extra-pages.ts";
export function bookNavigation(chapters: Chapter[], current?: Chapter): string {
  const groups: string[] = [];
  let part = "";
  for (const chapter of chapters) {
    if (chapter.part !== part) {
      if (part) groups.push("</ol></details>");
      part = chapter.part;
      groups.push(`<details class="book-part" open><summary>${part}</summary><ol>`);
    }
    const active = chapter === current ? ' class="current" aria-current="page"' : "";
    groups.push(`<li><a href="${chapter.slug}"${active}><span>${String(chapter.number).padStart(2, "0")}</span>${chapter.title}</a>`);
    if (chapter === current && chapter.toc.length > 0) {
      groups.push('<nav class="chapter-toc" aria-label="本章目录"><ol>');
      for (const item of chapter.toc) {
        groups.push(`<li><a href="#${item.id}"><span>${item.number}</span>${item.title}</a></li>`);
      }
      groups.push("</ol></nav>");
    }
    groups.push("</li>");
  }
  if (part) groups.push("</ol></details>");
  const extraLinks = [...EXTRA_PAGES, TERMS_PAGE]
    .map((page) => `<a href="${page.slug}.html">${page.title}</a>`)
    .join("");
  return `<div class="book-navigation">${groups.join("")}</div><div class="book-extras">${extraLinks}</div>`;
}
