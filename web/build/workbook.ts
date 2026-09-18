import { readFileSync } from "node:fs";
import * as cheerio from "cheerio";
import type { Chapter } from "./types.ts";
import { expandScientificNumbers } from "./dom.ts";
export function parseWorkbook(path: string, chapters: Chapter[]): void {
  const $ = cheerio.load(readFileSync(path, "utf8"), { xml: false });
  expandScientificNumbers($);
  const answers = new Map<number, string>();
  $(".my-solution").each((_, node) => {
    const label = $(node).attr("data-question") ?? "";
    const number = Number(label.slice(label.lastIndexOf("-") + 1));
    answers.set(number, $(node).html() ?? "");
  });
  let chapterIndex = -1;
  $(".chapterHead, .my-workbook-chapter, .my-exercise").each((_, node) => {
    const item = $(node);
    if (item.hasClass("my-workbook-chapter")) {
      chapterIndex = Number(item.attr("data-chapter")) - 1;
      return;
    }
    if (!item.hasClass("my-exercise") || chapterIndex < 0 || !chapters[chapterIndex]) return;
    const number = Number(item.attr("data-exercise"));
    const optional =
      (item.attr("data-level") ?? "") === "optional" ||
      item.find(".optional-marker, .marginnote").length > 0;
    item.find(".optional-marker").remove();
    chapters[chapterIndex].exercises.push({
      number: chapters[chapterIndex].exercises.length + 1,
      optional,
      question: item.html() ?? "",
      answer: answers.get(number) ?? "",
    });
  });
}
