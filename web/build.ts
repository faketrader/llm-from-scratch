import { cpSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT, OUT, WORK, CACHE, TEXTBOOK_WORK, WORKBOOK_WORK } from "./build/paths.ts";
import { ensurePdfInputs, conversion } from "./build/conversion.ts";
import { parseTextbook } from "./build/textbook.ts";
import { normalizeContent } from "./build/content.ts";
import { attachReferences, rewriteLinks, buildOwners } from "./build/references.ts";
import { parseWorkbook } from "./build/workbook.ts";
import { renderChapter, renderExtra, renderHome } from "./build/render.ts";
import { collectSearch, renderTerms } from "./build/indexes.ts";
import { copyAssets, copyVendorAssets, copyClientAssets } from "./build/assets.ts";
import { validateSite } from "./build/validate.ts";
import { EXTRA_PAGES, TERMS_PAGE } from "./build/extra-pages.ts";

function main(): void {
  ensurePdfInputs();
  mkdirSync(OUT, { recursive: true });
  mkdirSync(WORK, { recursive: true });
  mkdirSync(CACHE, { recursive: true });
  const textbookHtml = conversion("textbook", TEXTBOOK_WORK);
  const workbookHtml = conversion("workbook", WORKBOOK_WORK);
  const parsed = parseTextbook(textbookHtml);
  for (const chapter of parsed.chapters) normalizeContent(chapter);
  attachReferences(parsed.chapters, parsed.document);
  parseWorkbook(workbookHtml, parsed.chapters);
  rewriteLinks(parsed.chapters, buildOwners(parsed.chapters));

  for (const chapter of parsed.chapters) {
    writeFileSync(join(OUT, chapter.slug), renderChapter(chapter, parsed.chapters));
  }
  for (const page of EXTRA_PAGES) {
    writeFileSync(
      join(OUT, `${page.slug}.html`),
      renderExtra(page.title, parsed.extras.get(page.slug) ?? "", parsed.chapters),
    );
  }
  writeFileSync(
    join(OUT, `${TERMS_PAGE.slug}.html`),
    renderExtra(TERMS_PAGE.title, renderTerms(parsed.chapters), parsed.chapters),
  );
  writeFileSync(join(OUT, "index.html"), renderHome(parsed.chapters));
  writeFileSync(join(OUT, "search-index.json"), JSON.stringify(collectSearch(parsed.chapters)));
  writeFileSync(join(OUT, "book-manifest.json"), JSON.stringify(parsed.chapters.map((chapter) => ({
    chapter: chapter.number,
    title: chapter.title,
    sections: chapter.toc.length,
    exercises: chapter.exercises.length,
  })), null, 2));

  copyClientAssets();
  copyAssets(join(TEXTBOOK_WORK, "build"));
  copyAssets(join(WORKBOOK_WORK, "build"));
  cpSync(join(ROOT, "dist/textbook.pdf"), join(OUT, "textbook.pdf"));
  cpSync(join(ROOT, "dist/workbook.pdf"), join(OUT, "workbook.pdf"));
  copyVendorAssets();
  validateSite(OUT);
  console.log(`Published ${parsed.chapters.length} chapters`);
}

main();
