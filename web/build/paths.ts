import { resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

export const WEB = fileURLToPath(new URL("..", import.meta.url));
export const ROOT = resolve(WEB, "..");
export const OUT = join(ROOT, "dist/web");
export const WORK = join(ROOT, "build/web-work");
export const CACHE = join(ROOT, "build/web-cache");
export const CLIENT = join(WEB, "client");
export const TEMPLATES = join(WEB, "templates");
export const TEX4HT = join(WEB, "tex4ht");
export const TEXTBOOK_WORK = join(WORK, "textbook");
export const WORKBOOK_WORK = join(WORK, "workbook");
