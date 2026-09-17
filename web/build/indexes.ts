import * as cheerio from "cheerio";
import type { Chapter, SearchEntry } from "./types.ts";
export function collectSearch(chapters: Chapter[]): SearchEntry[] {
  const entries: SearchEntry[] = [];
  for (const chapter of chapters) {
    const $ = cheerio.load(`<main>${chapter.content}<section>${chapter.exercises.map((item) => item.question + item.answer).join("")}</section></main>`, null, false);
    $("p, h2, h3").each((_, node) => {
      const text = $(node).text().trim();
      if (!text) return;
      entries.push({
        url: chapter.slug + ($(node).attr("id") ? `#${$(node).attr("id")}` : ""),
        title: chapter.title,
        text,
      });
    });
  }
  return entries;
}
export function renderTerms(chapters: Chapter[]): string {
  const seen = new Set<string>();
  const terms: Array<{ zh: string; en: string; abbr: string; url: string }> = [];
  for (const chapter of chapters) {
    const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
    $(".term").each((_, node) => {
      const zh = $(node).find("strong").first().text().trim();
      const raw = $(node).find(".term-en").first().text().trim();
      const value = raw.startsWith("（") && raw.endsWith("）") ? raw.slice(1, -1) : raw;
      const comma = value.lastIndexOf("，");
      const en = comma >= 0 ? value.slice(0, comma) : value;
      const abbr = comma >= 0 ? value.slice(comma + 1) : "";
      const key = `${zh}\u0000${en}`;
      if (seen.has(key)) return;
      seen.add(key);
      const anchor = $(node).prev("a[id]").attr("id") ?? $(node).closest("[id]").attr("id") ?? "";
      terms.push({ zh, en, abbr, url: chapter.slug + (anchor ? `#${anchor}` : "") });
    });
  }
  terms.sort((a, b) => a.en.localeCompare(b.en, "en"));
  const rows = terms.map((term) => `<tr><td><a href="${term.url}">${term.zh}</a></td><td>${term.en}</td><td>${term.abbr}</td></tr>`).join("");
  return `<div class="table-scroll"><table><thead><tr><th>中文</th><th>英文</th><th>缩写</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}
