export type Chapter = {
  number: number;
  title: string;
  part: string;
  slug: string;
  label: string;
  content: string;
  toc: Array<{ id: string; number: string; title: string }>;
  references: string;
  exercises: Exercise[];
};

export type Exercise = {
  number: number;
  optional: boolean;
  question: string;
  answer: string;
};

export type SearchEntry = { url: string; title: string; text: string };
