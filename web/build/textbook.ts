import { readFileSync } from "node:fs";
import * as cheerio from "cheerio";
import type { Chapter } from "./types.ts";
import { cleanHeading, childHtml, expandScientificNumbers } from "./dom.ts";
import { extraPageSlugForSourceTitle } from "./extra-pages.ts";
export function parseTextbook(path: string): {
  chapters: Chapter[];
  extras: Map<string, string>;
  document: cheerio.CheerioAPI;
} {
  const $ = cheerio.load(readFileSync(path, "utf8"), { xml: false });
  expandScientificNumbers($);
  const chapters: Chapter[] = [];
  const extras = new Map<string, string>();
  let part = "";
  let pendingMeta: { slug: string; label: string; kind: "chapter" | "appendix"; order?: number } | undefined;
  let current: Chapter | undefined;
  let currentExtra: string | undefined;

  for (const node of $("body").contents().toArray()) {
    const element = $(node);
    const partHeading = element.is(".partHead")
      ? element
      : element.find(".partHead").first();
    if (partHeading.length > 0) {
      part = cleanHeading($, partHeading.get(0)!);
      current = undefined;
      currentExtra = undefined;
      continue;
    }

    const meta = element.is(".my-chapter-meta")
      ? element
      : element.find(".my-chapter-meta").first();
    if (meta.length > 0) {
      const kind = meta.attr("data-kind") === "appendix" ? "appendix" : "chapter";
      const order = Number(meta.attr("data-order"));
      pendingMeta = {
        slug: `${meta.attr("data-slug")}.html`,
        label: meta.attr("data-label") ?? "",
        kind,
        order: Number.isInteger(order) && order > 0 ? order : undefined,
      };
      continue;
    }

    const unitHeading = element.is(".chapterHead, .appendixHead")
      ? element
      : element.find(".chapterHead, .appendixHead").first();
    if (unitHeading.length > 0 && pendingMeta) {
      const number = chapters.length + 1;
      const displayNumber = pendingMeta.kind === "appendix"
        ? String.fromCharCode(64 + (pendingMeta.order ?? 1))
        : String(number);
      current = {
        number,
        displayNumber,
        kind: pendingMeta.kind,
        title: cleanHeading($, unitHeading.get(0)!),
        part,
        slug: pendingMeta.slug,
        label: pendingMeta.label,
        content: "",
        toc: [],
        references: "",
        exercises: [],
      };
      chapters.push(current);
      pendingMeta = undefined;
      currentExtra = undefined;
      continue;
    }

    const extraHeading = element.is(".likechapterHead")
      ? element
      : element.find(".likechapterHead").first();
    if (extraHeading.length > 0) {
      const title = cleanHeading($, extraHeading.get(0)!);
      currentExtra = extraPageSlugForSourceTitle(title);
      current = undefined;
      if (currentExtra) extras.set(currentExtra, "");
      continue;
    }

    if (element.is(".my-bibliography-start") || element.find(".my-bibliography-start").length > 0) {
      current = undefined;
      currentExtra = undefined;
      continue;
    }

    if (current) current.content += childHtml($, node);
    if (currentExtra) {
      extras.set(currentExtra, (extras.get(currentExtra) ?? "") + childHtml($, node));
    }
  }

  if (chapters.length === 0) throw new Error("make4ht produced no textbook chapters");
  return { chapters, extras, document: $ };
}
