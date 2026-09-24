import * as cheerio from "cheerio";
import type { AnyNode } from "domhandler";

export function normalizeTables($: cheerio.CheerioAPI): void {
  $("table.longtable").each((_, node) => {
    const table = $(node);
    // TeX4ht emits booktabs rules and longtable head/foot spacing as empty rows.
    table.children("tbody").children("tr").each((__, row) => {
      const item = $(row);
      if (!item.text().trim() && !item.find("img, svg, math, input, [rowspan], a[id]").length) {
        item.remove();
      }
    });
    if (!table.children("thead").length) {
      const header = table.children("tbody").children("tr").first();
      if (header.length) {
        header.children("td").each((__, cell) => {
          cell.tagName = "th";
          $(cell).attr("scope", "col");
        });
        const head = $("<thead></thead>").append(header);
        table.children("tbody").first().before(head);
      }
    }
  });
  $("table").each((_, table) => {
    if (!$(table).parent().hasClass("table-scroll")) {
      $(table).wrap('<div class="table-scroll"></div>');
    }
  });
}

export function shiftHeadings($: cheerio.CheerioAPI): void {
  $("h3").each((_, node) => { node.tagName = "h4"; });
  $("h2").not(".chapterHead").each((_, node) => { node.tagName = "h3"; });
  $("h1").each((_, node) => { node.tagName = "h2"; });
  // TeX4ht repeats the counter-based ID for unnumbered subsubsections.
  // Keep the first destination and give subsequent headings stable suffixes.
  const used = new Set<string>();
  const reserved = new Set($("[id]").toArray().map((node) => $(node).attr("id")!));
  $("h2[id], h3[id], h4[id]").each((_, node) => {
    const heading = $(node);
    const id = heading.attr("id")!;
    if (used.has(id)) {
      let suffix = 2;
      while (reserved.has(`${id}-${suffix}`)) suffix += 1;
      heading.attr("id", `${id}-${suffix}`);
      reserved.add(`${id}-${suffix}`);
    }
    used.add(id);
  });
}

export function cleanHeading($: cheerio.CheerioAPI, node: AnyNode): string {
  const clone = $(node).clone();
  clone.find(".titlemark, a").remove();
  clone.find("br").replaceWith(" ");
  return clone.text().replaceAll(" ", " ").trim();
}

export function childHtml($: cheerio.CheerioAPI, node: AnyNode): string {
  return $.html(node);
}

export function expandScientificNumbers($: cheerio.CheerioAPI): void {
  $(".mathjax-inline, .mathjax-env").contents().each((_, node) => {
    if (node.type !== "text") return;
    node.data = node.data.replace(
      /\\num\s*\{\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*[eEdD]\s*([+-]?\d+)\s*\}/g,
      (_, coefficient: string, exponent: string) => `${coefficient}\\times 10^{${exponent}}`,
    );
  });
}
