import Link from "next/link";
import { notFound } from "next/navigation";
import { getPage, getAdjacent, NAV } from "@/lib/guide-content";
import { BlockRenderer } from "@/components/user-guide/BlockRenderer";

export function generateStaticParams() {
  return Object.keys(getAllSlugsInternal()).map((slug) => ({
    slug: slug.split("/"),
  }));
}

function getAllSlugsInternal() {
  const slugs: Record<string, true> = {};
  NAV.forEach((sec) => sec.items.forEach((it) => { slugs[it.slug] = true; }));
  return slugs;
}

export default function GuidePage({ params }: { params: { slug: string[] } }) {
  const slug = params.slug.join("/");
  const page = getPage(slug);
  if (!page) notFound();

  const { prev, next } = getAdjacent(slug);

  const sectionLabel = page.section;

  return (
    <div>
      <nav className="mb-4 flex items-center gap-1 text-xs text-ink-500">
        <Link href="/user-guide" className="hover:text-ink-900">Hướng dẫn</Link>
        <span>/</span>
        <span className="text-ink-900">{sectionLabel}</span>
        <span>/</span>
        <span className="text-ink-900">{page.title}</span>
      </nav>

      <div className="mb-6 flex items-center gap-3">
        <span className="text-3xl">{page.icon}</span>
        <div>
          <h1 className="text-2xl font-extrabold text-ink-900">{page.title}</h1>
          <p className="mt-0.5 text-sm text-ink-700">{page.description}</p>
        </div>
      </div>

      <article className="rounded-card border border-ink-200 bg-white p-6 shadow-card lg:p-8">
        <BlockRenderer blocks={page.blocks} />
      </article>

      <div className="mt-6 flex items-center justify-between gap-4">
        {prev ? (
          <Link
            href={`/user-guide/${prev.slug}`}
            className="flex items-center gap-2 rounded-btn border border-ink-200 bg-white px-4 py-2.5 text-sm font-semibold text-ink-700 transition hover:border-ink-500 hover:text-ink-900"
          >
            ← {prev.title}
          </Link>
        ) : <div />}
        {next ? (
          <Link
            href={`/user-guide/${next.slug}`}
            className="flex items-center gap-2 rounded-btn border border-brand bg-brand-50 px-4 py-2.5 text-sm font-semibold text-brand transition hover:bg-brand hover:text-white"
          >
            {next.title} →
          </Link>
        ) : <div />}
      </div>
    </div>
  );
}
