import * as cheerio from "cheerio";
import type { Chapter } from "./types.ts";
import { publishFigure } from "./assets.ts";
import { shiftHeadings } from "./dom.ts";
export function normalizeContent(chapter: Chapter): void {
  const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
  $(".lfs-chapter-meta, .chapterHead").remove();
  $("figure.figure:has(> figure.figure)").each((_, node) => {
    const outer = $(node);
    const inner = outer.children("figure.figure").first();
    outer.replaceWith(inner);
  });
  $("p").each((_, node) => {
    const item = $(node);
    if (
      item.text().trim() === "" &&
      item.find("img, span.mathjax-env, a[id]").length === 0
    ) {
      item.remove();
    }
  });
  $("div.center").each((_, node) => {
    const item = $(node);
    if (item.find("img").length > 0 && item.find("figcaption").length > 0) {
      node.tagName = "figure";
      item.find("p").each((__, paragraph) => {
        if ($(paragraph).text().trim() === "" && $(paragraph).find("img").length === 0) {
          $(paragraph).remove();
        }
      });
      const image = item.find("img").first();
      image.attr("loading", "lazy");
      image.attr("alt", item.find("figcaption").text().trim());
    }
  });
  $("table").each((_, table) => {
    if (!$(table).parent().hasClass("table-scroll")) {
      $(table).wrap('<div class="table-scroll"></div>');
    }
  });
  $("img").each((_, node) => {
    const image = $(node);
    const source = image.attr("src") ?? "";
    image.attr("src", publishFigure(source));
  });
  $("figcaption .id").each((_, node) => {
    const number = $(node);
    const kind = number.closest("figure").hasClass("table-figure") ? "表" : "图";
    const text = number.text().replaceAll(" ", " ").trimStart();
    if (!text.startsWith(kind)) number.text(`${kind}${text}`);
  });
  $(".mathjax-equation").each((_, node) => {
    const equation = $(node);
    const anchor = equation.next("a[id]").first();
    const match = (anchor.attr("id") ?? "").match(/r(\d+)$/);
    if (!match) return;
    equation.wrap('<span class="equation-block"></span>');
    const block = equation.parent();
    block.prepend(anchor);
    block.append(
      $("<span>")
        .addClass("equation-number")
        .attr("aria-label", `公式 ${chapter.number}.${match[1]}`)
        .text(`(${chapter.number}.${match[1]})`),
    );
  });
  const admonitions = new Map([
    ["NOTE", "注记"],
    ["TIP", "提示"],
    ["IMPORTANT", "重要"],
    ["WARNING", "警告"],
    ["CAUTION", "注意"],
  ]);
  $(".algorithm-title").each((_, node) => {
    const title = $(node);
    if (/^\d+(?:\.\d+)+/.test(title.text().trim())) title.prepend("算法");
  });
  $(".tcolorbox").each((_, node) => {
    const box = $(node);
    const title = box.find(".tcolorbox-title").first();
    const titleText = title.text().trim();
    for (const [kind, label] of admonitions) {
      if (!titleText.startsWith(kind)) continue;
      box.addClass(`admonition ${kind.toLowerCase()}`);
      const detail = titleText.slice(kind.length).replace(/^：/, "").trim();
      title.empty().append($("<strong>").text(label));
      if (detail) title.append($("<span>").text(detail));
      break;
    }
    if (titleText.startsWith("算法")) box.addClass("algorithm");
  });
  $(".newtheorem:has(.lfs-example-label)").each((_, node) => {
    const example = $(node);
    example.find(".head").first().prepend("例 ");
    example.find(".lfs-example-label").remove();
    example.addClass("example");
  });
  shiftHeadings($);
  $("h2[id^='section-']").each((_, node) => {
    const heading = $(node);
    const id = heading.attr("id") ?? "";
    const number = id.slice("section-".length);
    const title = heading.clone().find("a").remove().end().text().trim();
    if (!heading.hasClass("unnumbered")) {
      heading.prepend(`<span class="section-number">${number}</span>`);
    }
    chapter.toc.push({ id, number, title });
  });
  const ids = new Set($("[id]").toArray().map((node) => $(node).attr("id")!));
  $("a[href^='#']").each((_, node) => {
    const link = $(node);
    const id = (link.attr("href") ?? "").slice(1);
    if (!id || ids.has(id)) return;
    const number = link.text().trim();
    const algorithmTitle = $(".algorithm-title").filter((__, title) =>
      $(title).text().trim().startsWith(`${number} `),
    ).first();
    if (algorithmTitle.length > 0) {
      algorithmTitle.closest("section.algorithm").attr("id", id);
      ids.add(id);
      return;
    }
    const caption = $("figcaption .id").filter((__, label) =>
      $(label).text().replaceAll(" ", " ").trim().startsWith(`${number}:`),
    ).first().closest("figcaption");
    if (caption.length > 0) {
      const figure = caption.closest("figure");
      (figure.length > 0 ? figure : caption).attr("id", id);
      ids.add(id);
    }
  });
  let passage = 0;
  $("p, h2, h3").each((_, node) => {
    passage += 1;
    if (!$(node).attr("id")) $(node).attr("id", `passage-${passage}`);
  });
  chapter.content = $("main").html() ?? "";
}
