import { readFileSync } from "node:fs";
import { join } from "node:path";
import * as cheerio from "cheerio";
import { TEMPLATES } from "./paths.ts";
import type { Chapter } from "./types.ts";
import { bookNavigation } from "./navigation.ts";
import { rewriteBookReferences } from "./references.ts";
import { clientAssetVersion } from "./assets.ts";
import { shiftHeadings } from "./dom.ts";
import { pdfFileName } from "./version.ts";

function updatePdfLinks($: cheerio.CheerioAPI): void {
  for (const book of ["textbook", "workbook"] as const) {
    $(`a[href='${book}.pdf']`).attr("href", pdfFileName(book));
  }
}

function template(name: string): string {
  return readFileSync(join(TEMPLATES, name), "utf8");
}

function page(contentTemplate?: string): cheerio.CheerioAPI {
  const $ = cheerio.load(template("layout.html"));
  if (contentTemplate) $("main#chapter").html(template(contentTemplate));
  updatePdfLinks($);
  for (const name of ["styles.css", "mathjax-config.js", "app.js"]) {
    const attribute = name.endsWith(".css") ? "href" : "src";
    $(`[${attribute}='${name}']`).attr(attribute, `${name}?v=${clientAssetVersion(name)}`);
  }
  return $;
}

export function renderChapter(chapter: Chapter, chapters: Chapter[]): string {
  const $ = page("chapter.html");
  const designation = chapter.kind === "appendix"
    ? `附录${chapter.displayNumber}`
    : `第${chapter.displayNumber}章`;
  const sidebarNumber = chapter.kind === "appendix"
    ? chapter.displayNumber
    : chapter.displayNumber.padStart(2, "0");
  $("title").text(`${chapter.title} · 大语言模型：从理论到实践`);
  $("meta[name='description']").attr("content", `《大语言模型：从理论到实践》${designation}${chapter.title}，含教材正文、公式图表和配套材料。`);
  $(".sidebar-intro p").text(chapter.part);
  $(".chapter-current span").text(sidebarNumber);
  $(".chapter-current strong").text(chapter.title);
  $("#sidebar > nav").replaceWith(`<nav class="all-book-navigation" aria-label="全书目录">${bookNavigation(chapters, chapter)}</nav>`);
  $(".breadcrumb").html(`教材 <span>/</span> ${chapter.part}`);
  $(".chapter-heading .eyebrow").text(chapter.kind === "appendix" ? `APPENDIX ${chapter.displayNumber}` : `CHAPTER ${sidebarNumber}`);
  $(".chapter-heading").attr("id", chapter.label);
  $(".chapter-heading h1").text(chapter.title);
  $(".chapter-heading .chapter-subtitle").remove();
  $("#chapter-content").html(chapter.content);
  const exercises = chapter.exercises.map((exercise) => {
    const optional = exercise.optional ? '<span class="optional">选修</span>' : "";
    return `<div class="exercise" id="exercise-${exercise.number}"><div class="exercise-heading">习题 ${chapter.displayNumber}.${exercise.number}${optional}</div>${exercise.question}<details><summary>展开参考解析</summary><div class="answer">${exercise.answer}</div></details></div>`;
  });
  const exerciseSection = $("#exercises");
  exerciseSection.find(".exercise").remove();
  if (exercises.length > 0) exerciseSection.append(exercises.join(""));
  else {
    exerciseSection.remove();
    $(".sidebar-bottom a[href='#exercises'], .reading-tools a[href='#exercises']").remove();
  }
  if (chapter.references) $("#references").append(chapter.references);
  else {
    $("#references").remove();
    $(".sidebar-bottom a[href='#references']").remove();
  }
  const pager: string[] = ['<div class="chapter-pager">'];
  const previous = chapters[chapter.number - 2];
  const next = chapters[chapter.number];
  pager.push(previous ? `<a href="${previous.slug}">← ${previous.title}</a>` : "<span></span>");
  pager.push(next ? `<a href="${next.slug}">${next.title} →</a>` : "<span></span>");
  pager.push("</div>");
  $("main > footer").before(pager.join(""));
  return $.html();
}

export function renderExtra(title: string, content: string, chapters: Chapter[]): string {
  if (!content.trim()) throw new Error(`Missing content for extra page: ${title}`);
  const $ = page("extra.html");
  const article = cheerio.load(content, null, false);
  shiftHeadings(article);
  $("title").text(`${title} · 大语言模型`);
  $(".chapter-current span").remove();
  $(".chapter-current strong").text(title);
  $("#sidebar > nav").replaceWith(`<nav class="all-book-navigation" aria-label="全书目录">${bookNavigation(chapters)}</nav>`);
  $(".sidebar-bottom a, .reading-tools a[href='#exercises']").remove();
  $(".chapter-heading h1").text(title);
  $("#chapter-content").html(article.root().html() ?? "");
  rewriteBookReferences($, chapters);
  return $.html();
}

export function renderHome(chapters: Chapter[]): string {
  const $ = page();
  $("title").text("全书目录 · 大语言模型：从理论到实践");
  $("meta[name='description']").attr("content", "《大语言模型：从理论到实践》开放教材，覆盖模型、训练、推理、应用系统与多模态方法，并提供配套习题与 PDF。");
  $("body").addClass("home-body");
  $("#sidebar, .reading-tools").remove();
  $("main#chapter").html(template("home.html")
    .replaceAll("{{firstChapter}}", chapters[0].slug)
    .replaceAll("{{navigation}}", bookNavigation(chapters)));
  updatePdfLinks($);
  $("#menu-toggle").remove();
  return $.html();
}
