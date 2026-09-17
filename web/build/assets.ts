import { cpSync, existsSync, readdirSync, readFileSync, statSync, rmSync, writeFileSync } from "node:fs";
import { basename, extname, join, resolve } from "node:path";
import { WEB, ROOT, OUT, CACHE, CLIENT } from "./paths.ts";
import { inputFingerprint } from "./files.ts";
import { createHash } from "node:crypto";

// The explicit order preserves the reader cascade, then adds book and home rules.
const styles = ["reader", "content", "interactions", "responsive", "navigation", "highlighting", "home"];

function clientAsset(name: string): string {
  if (name === "styles.css") {
    return styles.map((part) => readFileSync(join(CLIENT, "styles", `${part}.css`), "utf8")).join("\n");
  }
  return readFileSync(join(CLIENT, name), "utf8");
}

export function clientAssetVersion(name: string): string {
  // Include imported modules so a reader update invalidates the whole module graph.
  const content = name === "app.js"
    ? ["app.js", "reading.js", "search.js", "figures.js"].map(clientAsset).join("\n")
    : clientAsset(name);
  return createHash("sha256").update(content).digest("hex").slice(0, 12);
}

export function copyClientAssets(): void {
  for (const name of ["styles.css", "mathjax-config.js", "app.js", "reading.js", "search.js", "figures.js"]) {
    let content = clientAsset(name);
    if (name === "app.js") {
      content = content.replace(/from "\.\/(reading|search|figures)\.js"/g,
        (_, module: string) => `from "./${module}.js?v=${clientAssetVersion("app.js")}"`);
    }
    writeFileSync(join(OUT, name), content);
  }
}
export function copyAssets(source: string): void {
  for (const name of readdirSync(source)) {
    const path = join(source, name);
    if (!statSync(path).isFile()) continue;
    if ([".svg", ".png", ".jpg", ".jpeg", ".webp"].includes(extname(name).toLowerCase())) {
      cpSync(path, join(OUT, basename(name)));
    }
  }
}

export function copyVendorAssets(): void {
  const packages = [
    [join(WEB, "node_modules/mathjax"), join(OUT, "vendor/mathjax")],
    [join(WEB, "node_modules/@mathjax/mathjax-newcm-font"), join(OUT, "vendor/fonts")],
    [join(WEB, "node_modules/@highlightjs/cdn-assets"), join(OUT, "vendor/highlight")],
  ] as const;
  const fingerprint = inputFingerprint([join(WEB, "pnpm-lock.yaml")]);
  const stamp = join(CACHE, "vendor.sha256");
  if (
    existsSync(stamp) &&
    readFileSync(stamp, "utf8") === fingerprint &&
    packages.every(([, target]) => existsSync(target))
  ) {
    console.log("Reusing web vendor assets");
    return;
  }
  rmSync(join(OUT, "vendor"), { recursive: true, force: true });
  for (const [source, target] of packages) cpSync(source, target, { recursive: true });
  writeFileSync(stamp, fingerprint);
}

/** Replace TeX4ht's PDF image placeholder with the SVG built from the same TikZ source. */
export function publishFigure(source: string): string {
  if (!source.endsWith("-.png")) return source;
  const pdf = resolve(ROOT, "book/textbook", source.slice(0, -"-.png".length) + ".pdf");
  if (!existsSync(pdf)) return source;
  const target = `${basename(pdf, ".pdf")}.svg`;
  const output = join(OUT, target);
  if (!existsSync(output)) throw new Error(`Missing web figure ${target}; run make web-figures first`);
  return target;
}
