import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT } from "./paths.ts";

const preamble = readFileSync(join(ROOT, "book/preamble.tex"), "utf8");
const fields = new Map(
  [...preamble.matchAll(/^\\newcommand\*\{\\bookversion(major|minor|patch|date)\}\{(\d+)\}$/gm)]
    .map((match) => [match[1], match[2]]),
);
const parts = ["major", "minor", "patch", "date"].map((field) => {
  const value = fields.get(field);
  if (!value) throw new Error(`Missing book version field: ${field}`);
  return value;
});

export const bookVersion = `${parts[0]}.${parts[1]}.${parts[2]}-${parts[3]}`;
export function pdfFileName(book: "textbook" | "workbook"): string {
  return `${book}-${bookVersion}.pdf`;
}
