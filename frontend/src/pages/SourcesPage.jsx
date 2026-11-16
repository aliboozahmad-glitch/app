import { useLang } from "@/i18n/LanguageContext";
import { usePublic } from "@/lib/api";
import { Sources } from "@/components/genova/ResultView";
import { TierLegend } from "./Dashboard";

const IMG = "https://images.unsplash.com/photo-1628595351029-c2bf17511435?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600";

const DiseaseRow = ({ d, t, refs }) => (
  <div className="bg-white border border-slate-200 rounded-md p-5 space-y-3" data-testid={`source-disease-${d.id}`}>
    <div className="flex flex-wrap items-baseline gap-x-3">
      <h3 className="font-semibold text-lg">{d.name}</h3>
      <span className="font-mono-genes text-sm text-slate-500">{d.gene}</span>
      <span className="text-sm text-slate-600">· {d.inheritance_label}</span>
    </div>
    <div>
      <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-1">{t.sources.regional}</div>
      <ul className="text-sm space-y-1">
        {d.regional.map((r, i) => (
          <li key={i} className="flex flex-wrap gap-2">
            <span className={`text-xs px-2 py-0.5 rounded border ${r.status === "validated" ? "bg-emerald-50 border-emerald-200 text-emerald-800" : "bg-amber-50 border-amber-200 text-amber-800"}`}>
              {r.status === "validated" ? t.sources.validated : t.sources.draft}
            </span>
            <span className="font-medium">{r.region_label}</span>
            <span className="text-slate-400">· {refs[r.source]?.publisher}</span>
          </li>
        ))}
      </ul>
    </div>
  </div>
);

export default function SourcesPage() {
  const { t } = useLang();
  const catalog = usePublic("/catalog");
  const refsData = usePublic("/references");
  const refs = Object.fromEntries((refsData?.references || []).map((r) => [r.id, r]));
  return (
    <div>
      <div className="relative h-56 sm:h-64 overflow-hidden bg-slate-900">
        <img src={IMG} alt="" className="absolute inset-0 w-full h-full object-cover opacity-40" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-8 h-full flex flex-col justify-end pb-8 text-white">
          <div className="text-xs uppercase tracking-[0.2em] font-semibold text-slate-300">{t.sources.overline}</div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mt-2" data-testid="sources-title">{t.sources.title}</h1>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 space-y-10">
        <p className="text-slate-700 max-w-3xl">{t.sources.subtitle}</p>
        <TierLegend />
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">{t.sources.panel}</h2>
          <div className="grid lg:grid-cols-2 gap-4">{catalog?.diseases.map((d) => <DiseaseRow key={d.id} d={d} t={t} refs={refs} />)}</div>
          {catalog && <p className="text-xs font-mono-genes text-slate-400">{catalog.engine_version} · {catalog.data_version}</p>}
        </section>
        <section className="bg-white border border-slate-200 rounded-md p-6">
          <Sources refs={refsData?.references || []} />
        </section>
      </div>
    </div>
  );
}
