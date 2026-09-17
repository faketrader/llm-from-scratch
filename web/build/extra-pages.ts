export type ExtraPage = {
  slug: string;
  title: string;
  sourceTitles: readonly string[];
};

export const EXTRA_PAGES = [
  { slug: "preface", title: "前言", sourceTitles: ["前言"] },
  { slug: "reading-guide", title: "阅读说明", sourceTitles: ["阅读说明"] },
  {
    slug: "notation",
    title: "符号与数学约定",
    sourceTitles: ["符号与数学约定", "符号及数学约定"],
  },
] as const satisfies readonly ExtraPage[];

export const TERMS_PAGE = {
  slug: "terms",
  title: "中英文术语索引",
} as const;

const extraPageSlugBySourceTitle = new Map<string, string>(
  EXTRA_PAGES.flatMap((page) => page.sourceTitles.map((title) => [title, page.slug] as const)),
);

export function extraPageSlugForSourceTitle(title: string): string | undefined {
  return extraPageSlugBySourceTitle.get(title);
}
