import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, resolve, sep } from "node:path";
import * as cheerio from "cheerio";
import type { SearchEntry } from "./types.ts";

/** Check the published DOM and local destinations without requesting external sites. */
export function validateSite(directory: string): void {
  const root = resolve(directory);
  const pages = new Map<string, { ids: Set<string>; document: cheerio.CheerioAPI }>();
  const failures = new Set<string>();
  for (const name of readdirSync(root).filter((name) => name.endsWith(".html"))) {
    const html = readFileSync(join(root, name), "utf8");
    const $ = cheerio.load(html);
    const ids = new Set<string>();
    $("[id]").each((_, node) => {
      const id = $(node).attr("id")!;
      if (ids.has(id)) failures.add(`${name}: duplicate id ${id}`);
      ids.add(id);
    });
    if ($("main").length !== 1 || $("main h1").length !== 1) {
      failures.add(`${name}: expected one main and one page heading`);
    }
    if (/@@\w+@@|\{\{(?:firstChapter|chapterCount|exerciseCount|navigation)\}\}/.test(html)) {
      failures.add(`${name}: unresolved template field`);
    }
    pages.set(name, { ids, document: $ });
  }
  if (!pages.has("index.html")) failures.add("Missing index.html");

  function checkLink(source: string, value: string): void {
    if (!value || /^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(value)) return;
    try {
      const url = new URL(value, `https://book.invalid/${source}`);
      const filename = decodeURIComponent(url.pathname).slice(1) || "index.html";
      const path = resolve(root, filename);
      if (!path.startsWith(root + sep) || !existsSync(path) || !statSync(path).isFile()) {
        failures.add(`${source}: missing local file ${value}`);
        return;
      }
      const id = decodeURIComponent(url.hash.slice(1));
      if (id && pages.has(filename) && !pages.get(filename)!.ids.has(id)) {
        failures.add(`${source}: missing anchor ${value}`);
      }
    } catch {
      failures.add(`${source}: invalid URL ${value}`);
    }
  }

  for (const [name, { document: $ }] of pages) {
    $("a[href], link[href], script[src], img[src], source[src]").each((_, node) => {
      checkLink(name, $(node).attr("href") ?? $(node).attr("src") ?? "");
    });
    // The dialog image receives its source when the reader opens a figure.
    $("img:not(#figure-large)").each((_, node) => {
      if (!$(node).attr("src")) failures.add(`${name}: image has no source`);
    });
  }
  const searchPath = join(root, "search-index.json");
  if (!existsSync(searchPath)) failures.add("Missing search-index.json");
  else {
    const entries: SearchEntry[] = JSON.parse(readFileSync(searchPath, "utf8"));
    for (const entry of entries) {
      if (!entry.url || !entry.title || !entry.text) failures.add("Invalid search entry");
      else checkLink("search-index.json", entry.url);
    }
  }
  if (failures.size > 0) {
    throw new Error(`Web validation failed (${failures.size}):\n${[...failures].join("\n")}`);
  }
  console.log(`Validated ${pages.size} pages, local links, anchors, resources and search destinations`);
}
