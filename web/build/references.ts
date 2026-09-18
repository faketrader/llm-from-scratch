import * as cheerio from "cheerio";
import type { Chapter } from "./types.ts";
export function attachReferences(chapters: Chapter[], document: cheerio.CheerioAPI): void {
  const entries = new Map<string, string>();
  document("dt.thebibliography").each((_, node) => {
    const id = document(node).attr("id");
    const term = document(node).clone();
    const detail = document(node).nextAll("dd.thebibliography").first().clone();
    if (id && detail.length > 0) {
      for (const fragment of [term, detail]) {
        fragment.find("a[href='textbook.html']").remove();
        fragment.find("a.url").each((__, link) => {
          const item = document(link);
          const href = item.attr("href") ?? "";
          if (href && !href.includes(":") && !href.includes("/")) {
            item.attr("href", `https://arxiv.org/abs/${href}`);
          }
        });
      }
      entries.set(id, document.html(term.get(0)) + document.html(detail.get(0)));
    }
  });
  for (const chapter of chapters) {
    const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
    const used = new Set<string>();
    const backLinks = new Map<string, string>();
    $("a[href*='#X']").each((_, link) => {
      const item = $(link);
      const href = item.attr("href") ?? "";
      const hash = href.lastIndexOf("#");
      if (hash < 0) return;
      const id = href.slice(hash + 1);
      used.add(id);
      item.attr("href", `#${id}`);
      if (!backLinks.has(id)) {
        const citationId = `cite-${id}`;
        item.attr("id", citationId);
        backLinks.set(id, citationId);
      }
    });
    const selected = [...used].flatMap((id) => {
      const entry = entries.get(id);
      const citationId = backLinks.get(id);
      if (!entry || !citationId) return [];
      const reference = cheerio.load(entry, null, false);
      const term = reference("dt.thebibliography");
      const label = term.text().trim();
      term.empty().append(
        reference("<a>")
          .attr("href", `#${citationId}`)
          .attr("aria-label", `返回正文中的引文 ${label}`)
          .text(label),
      );
      return [reference.root().html() ?? ""];
    });
    chapter.references = selected.length > 0 ? `<dl class="thebibliography">${selected.join("")}</dl>` : "";
    chapter.content = $("main").html() ?? "";
  }
}

export function buildOwners(chapters: Chapter[]): Map<string, Chapter> {
  const owners = new Map<string, Chapter>();
  for (const chapter of chapters) {
    const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
    $("[id]").each((_, node) => { owners.set($(node).attr("id")!, chapter); });
  }
  return owners;
}

export function rewriteBookReferences($: cheerio.CheerioAPI, chapters: Chapter[]): void {
  const chapterByLabel = new Map(chapters.map((chapter) => [chapter.label, chapter]));
  $(".my-bookxref[data-label]").each((_, node) => {
    const link = $(node);
    const target = chapterByLabel.get(link.attr("data-label") ?? "");
    if (!target) return;
    const text: string[] = [];
    let sibling = node.nextSibling;
    while (sibling) {
      const next = sibling.nextSibling;
      if (sibling.type === "text" && sibling.data.trim() === "") {
        sibling = next;
        continue;
      }
      const fragment = $(sibling);
      if (sibling.type !== "tag" || !fragment.is("a[href^='#']")) break;
      text.push(fragment.text());
      fragment.remove();
      sibling = next;
    }
    const reference = link.text() + text.join("");
    const title = reference.includes(target.title) ? `《${target.title}》` : "";
    const designation = target.kind === "appendix"
      ? `附录${target.displayNumber}`
      : `第${target.displayNumber}章`;
    link.text(`${designation}${title}`);
    link.attr("href", `${target.slug}#${target.label}`);
    link.removeAttr("data-label");
  });
}

export function rewriteLinks(chapters: Chapter[], owners: Map<string, Chapter>): void {
  for (const chapter of chapters) {
    const $ = cheerio.load(`<main>${chapter.content}</main>`, null, false);
    rewriteBookReferences($, chapters);
    $("a[href^='#']").each((_, node) => {
      const link = $(node);
      const href = link.attr("href")!;
      const owner = owners.get(href.slice(1));
      if (owner && owner !== chapter) link.attr("href", owner.slug + href);
    });
    chapter.content = $("main").html() ?? "";
  }
}
