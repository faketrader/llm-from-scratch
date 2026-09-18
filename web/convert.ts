import { mkdirSync } from "node:fs";
import { CACHE, TEXTBOOK_WORK, WORK, WORKBOOK_WORK } from "./build/paths.ts";
import { conversion } from "./build/conversion.ts";

function main(): void {
  mkdirSync(WORK, { recursive: true });
  mkdirSync(CACHE, { recursive: true });
  conversion("textbook", TEXTBOOK_WORK);
  conversion("workbook", WORKBOOK_WORK);
  console.log("Prepared textbook and workbook web conversions");
}

main();
