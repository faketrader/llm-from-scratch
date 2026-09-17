import { existsSync, readdirSync, readFileSync, statSync, mkdirSync, writeFileSync } from "node:fs";
import { extname, join } from "node:path";
import { ROOT, CACHE, TEX4HT } from "./paths.ts";
import { filesUnder, inputFingerprint, run } from "./files.ts";
export function ensurePdfInputs(): void {
  const missing = ["textbook.pdf", "workbook.pdf"]
    .map((name) => join(ROOT, "dist", name))
    .filter((path) => !existsSync(path));
  if (missing.length > 0) {
    throw new Error(`Missing delivery PDFs; run make books first: ${missing.join(", ")}`);
  }
}

function conversionInputs(entry: "textbook" | "workbook"): string[] {
  const shared = readdirSync(join(ROOT, "book"))
    .map((name) => join(ROOT, "book", name))
    .filter((path) => statSync(path).isFile());
  const inputs = [
    ...shared,
    ...filesUnder(join(ROOT, "book", entry)),
    join(TEX4HT, "tex4ht.cfg"),
    join(TEX4HT, "make4ht.mk4"),
  ];
  if (entry === "textbook") inputs.push(...filesUnder(join(ROOT, "book", "figures")));
  const sourceExtensions = new Set([".tex", ".sty", ".bib", ".ist", ".cfg", ".mk4", ".pdf", ".png", ".jpg", ".jpeg", ".svg"]);
  return [...new Set(inputs)].filter((path) => sourceExtensions.has(extname(path))).sort();
}

function convertBook(entry: "textbook" | "workbook", work: string): string {
  const sourceDir = join(ROOT, "book", entry);
  const buildDir = join(work, "build");
  mkdirSync(buildDir, { recursive: true });
  run(
    "make4ht",
    [
      "-x",
      "-f",
      "html5-common_domfilters",
      "-a",
      "warning",
      "-c",
      join(TEX4HT, "tex4ht.cfg"),
      "-e",
      join(TEX4HT, "make4ht.mk4"),
      "-B",
      buildDir,
      `${entry}.tex`,
      "mathjax",
    ],
    sourceDir,
  );
  const log = readFileSync(join(buildDir, `${entry}.log`), "utf8");
  if (/^!/m.test(log)) throw new Error(`${entry} web conversion has TeX errors; inspect ${buildDir}/${entry}.log`);
  for (const failure of [
    "undefined on input line",
    "Citation '",
  ]) {
    if (log.includes(failure)) {
      throw new Error(`${entry} web conversion failed validation: ${failure}`);
    }
  }
  return join(buildDir, `${entry}.html`);
}

export function conversion(entry: "textbook" | "workbook", work: string): string {
  const html = join(work, "build", `${entry}.html`);
  const fingerprint = inputFingerprint(conversionInputs(entry));
  const stamp = join(CACHE, `${entry}.sha256`);
  if (existsSync(html) && existsSync(stamp) && readFileSync(stamp, "utf8") === fingerprint) {
    console.log(`Reusing ${entry} web conversion`);
    return html;
  }
  const output = convertBook(entry, work);
  mkdirSync(CACHE, { recursive: true });
  writeFileSync(stamp, fingerprint);
  return output;
}
