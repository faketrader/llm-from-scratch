import { createReadStream, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("../dist/web", import.meta.url)));
const host = "127.0.0.1";
const port = Number(process.env.PORT ?? 8765);
const contentTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".pdf", "application/pdf"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".woff2", "font/woff2"],
]);

createServer((request, response) => {
  const requestPath = new URL(request.url ?? "/", `http://${host}:${port}`).pathname;
  let relativePath = normalize(decodeURIComponent(requestPath));
  while (relativePath.startsWith("/") || relativePath.startsWith("\\")) {
    relativePath = relativePath.slice(1);
  }
  let filePath = resolve(join(root, relativePath || "index.html"));
  if (filePath !== root && !filePath.startsWith(root + sep)) {
    response.writeHead(403).end("Forbidden");
    return;
  }
  try {
    if (statSync(filePath).isDirectory()) filePath = join(filePath, "index.html");
    const size = statSync(filePath).size;
    response.writeHead(200, {
      "Content-Length": size,
      "Content-Type": contentTypes.get(extname(filePath).toLowerCase()) ?? "application/octet-stream",
    });
    createReadStream(filePath).pipe(response);
  } catch {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("Not Found");
  }
}).listen(port, host, () => {
  console.log(`Serving ${root} at http://${host}:${port}`);
});
