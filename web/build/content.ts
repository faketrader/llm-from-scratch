import * as cheerio from "cheerio";
import type { Chapter } from "./types.ts";
import { publishFigure } from "./assets.ts";
import { shiftHeadings } from "./dom.ts";
export function normalizeContent(chapter: Chapter): void {
  const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
  $(".my-chapter-meta, .chapterHead").remove();
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
        .attr("aria-label", `公式 ${chapter.displayNumber}.${match[1]}`)
        .text(`(${chapter.displayNumber}.${match[1]})`),
    );
  });
  const admonitions = new Map([
    ["note", "注记"],
    ["tip", "提示"],
    ["important", "重要"],
    ["warning", "警告"],
    ["caution", "注意"],
    ["assumption", "前提"],
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
      if (!box.hasClass(kind)) continue;
      box.addClass(`admonition ${kind === "assumption" ? "important" : kind}`);
      const detail = titleText.slice(label.length).replace(/^：/, "").trim();
      title.empty().append($("<strong>").text(label));
      if (detail) title.append($("<span>").text(detail));
      break;
    }
    if (titleText.startsWith("算法")) box.addClass("algorithm");
  });
  const theoremKinds = new Map([
    ["theorem", "定理"],
    ["lemma", "引理"],
    ["proposition", "命题"],
    ["corollary", "推论"],
    ["definition", "定义"],
    ["example", "例"],
    ["remark", "注"],
  ]);
  $(".newtheorem:has(.my-theorem-kind)").each((_, node) => {
    const statement = $(node);
    const marker = statement.find(".my-theorem-kind").first();
    const kind = marker.attr("data-kind") ?? "";
    const label = theoremKinds.get(kind);
    if (label) statement.find(".head").first().prepend(`${label} `);
    marker.remove();
    if (kind) statement.addClass(kind);
  });
  shiftHeadings($);
  $("h2[id^='section-'], h3[id^='section-']").each((_, node) => {
    const heading = $(node);
    const id = heading.attr("id") ?? "";
    const number = id.slice("section-".length);
    const title = heading.clone().find("a").remove().end().text().trim();
    if (!heading.hasClass("unnumbered")) {
      heading.prepend(`<span class="section-number">${number}</span>`);
    }
    if (node.tagName === "h2") chapter.toc.push({ id, number, title });
  });
  // A marker at the start of a section applies to the entire section.
  // Move only markers in the heading's immediate sibling paragraph.
  $("h2, h3, h4").each((_, node) => {
    const heading = $(node);
    const paragraph = heading.next("p");
    const marker = paragraph.children(".optional-marker").first();
    if (!marker.length) return;
    const contents = paragraph.contents();
    const prefix = contents.slice(0, contents.toArray().indexOf(marker[0])).text();
    if (prefix.trim()) return;
    marker.attr("aria-label", "本节选读，含下属小节");
    marker.attr("title", "本节正文及下属小节可延后阅读");
    marker.children("span").last().text("本节选读");
    heading.append(marker);
    if (!paragraph.text().trim() && !paragraph.children().length) paragraph.remove();
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
