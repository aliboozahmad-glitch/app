import PropTypes from "prop-types";
import { useLang } from "@/i18n/LanguageContext";
import { usePublic } from "@/lib/api";
import { Sources } from "@/components/genova/ResultView";
import { LoadState } from "@/components/genova/LoadState";
import { TierLegend } from "./Dashboard";

const IMG = "https://images.unsplash.com/photo-1628595351029-c2bf17511435?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600";

const StatusTag = ({ status }) => {
  const { t } = useLang();
  const ok = status === "validated";
  return (
    <span className={`text-xs px-2 py-0.5 rounded border ${ok ? "bg-emerald-50 border-emerald-200 text-emerald-800" : "bg-amber-50 border-amber-200 text-amber-800"}`}>
      {ok ? t.sources.validated : t.sources.draft}
    </span>
  );
};

StatusTag.propTypes = { status: PropTypes.string.isRequired };

const DiseaseRow = ({ d, refs }) => {
  const { t } = useLang();
  return (
    <div className="bg-white border border-slate-200 rounded-md p-5 space-y-3" data-testid={`source-disease-${d.id}`}>
      <div className="flex flex-wrap items-baseline gap-x-3">
        <h3 className="font-semibold text-lg">{d.name}</h3>
        <span className="font-mono-genes text-sm text-slate-500">{d.gene}</span>
        <span className="text-sm text-slate-600">· {d.inheritance_label}</span>
      </div>
      <div>
        <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-1">{t.sources.regional}</div>
        <ul className="text-sm space-y-1">
          {d.regional.map((r) => (
            <li key={`${r.region}-${r.source}`} className="flex flex-wrap gap-2">
              <StatusTag status={r.status} />
              <span className="font-medium">{r.region_label}</span>
              <span className="text-slate-400">· {refs[r.source]?.publisher}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

DiseaseRow.propTypes = {
  d: PropTypes.shape({
    id: PropTypes.string.isRequired, name: PropTypes.string.isRequired, gene: PropTypes.string,
    inheritance_label: PropTypes.string, regional: PropTypes.arrayOf(PropTypes.object).isRequired,
  }).isRequired,
  refs: PropTypes.object.isRequired,
};

export default function SourcesPage() {
  const { t } = useLang();
  const catalogState = usePublic("/catalog");
  const refsState = usePublic("/references");
  const refs = Object.fromEntries((refsState.data?.references || []).map((r) => [r.id, r]));
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
          <LoadState state={catalogState} testId="sources-catalog">
            {(catalog) => (
              <>
                <div className="grid lg:grid-cols-2 gap-4">{catalog.diseases.map((d) => <DiseaseRow key={d.id} d={d} refs={refs} />)}</div>
                <p className="text-xs font-mono-genes text-slate-400">{catalog.engine_version} · {catalog.data_version}</p>
              </>
            )}
          </LoadState>
        </section>
        <section className="bg-white border border-slate-200 rounded-md p-6">
          <LoadState state={refsState} testId="sources-references">{(data) => <Sources refs={data.references} />}</LoadState>
        </section>
      </div>
    </div>
  );
}
