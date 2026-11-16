import { ExternalLink } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { CertaintyBadge } from "./primitives";
import { OutcomeTable } from "./OutcomeTable";
import { PunnettGrid } from "./PunnettGrid";
import { Scenarios } from "./Scenarios";

const NoteList = ({ title, items, testId }) => (
  <div data-testid={testId}>
    <h3 className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-2">{title}</h3>
    <ul className="space-y-1.5 text-sm text-slate-700 list-disc ps-5">
      {items.map((i) => <li key={i.key}>{i.text}</li>)}
    </ul>
  </div>
);

export const Sources = ({ refs }) => {
  const { t } = useLang();
  return (
    <div data-testid="result-references">
      <h3 className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-2">{t.c.references}</h3>
      <ol className="space-y-2 text-sm">
        {refs.map((r, i) => (
          <li key={r.id} className="flex gap-2">
            <span className="font-mono-genes text-slate-400">[{i + 1}]</span>
            <span>
              <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-slate-900 underline underline-offset-2 hover:text-slate-600" data-testid={`reference-link-${r.id}`}>
                {r.title}<ExternalLink size={12} className="inline ms-1" />
              </a>
              <span className="text-slate-500"> · {r.publisher} · {r.link_check === "verified_2026_06" ? t.c.verified : t.c.manual}</span>
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
};

export const ResultView = ({ analysis }) => {
  const { t } = useLang();
  const r = analysis.result;
  const d = r.details || {};
  return (
    <section className="bg-white border border-slate-200 rounded-md shadow-sm rise" data-testid="result-card">
      <div className="p-6 sm:p-8 border-b border-slate-200 flex flex-wrap items-start gap-3 justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500">{t.c.result}{d.disease_name ? ` · ${d.disease_name}` : ""}</div>
          <p className="mt-1 text-slate-900 font-medium" data-testid="result-method">{t.c.method}: {r.method_label}</p>
          {d.inheritance_label && <p className="text-sm text-slate-500" data-testid="result-inheritance">{d.inheritance_label}</p>}
          {d.mechanism_text && <p className="text-sm text-slate-600 mt-2 max-w-2xl" data-testid="result-mechanism">{d.mechanism_text}</p>}
        </div>
        <CertaintyBadge tier={r.certainty} label={r.certainty_label} />
      </div>
      <div className="p-6 sm:p-8 space-y-8">
        {r.outcomes.length > 0 && <OutcomeTable result={r} />}
        {d.scenarios && r.method !== "carrier_exact" && <Scenarios details={d} />}
        {d.grid && <PunnettGrid grid={d.grid} />}
        <div className="grid md:grid-cols-2 gap-8">
          <NoteList title={t.c.assumptions} items={r.assumptions} testId="result-assumptions" />
          <NoteList title={t.c.limitations} items={r.limitations} testId="result-limitations" />
        </div>
        <Sources refs={r.references} />
        <div className="text-xs text-slate-400 font-mono-genes flex flex-wrap gap-4" data-testid="result-versions">
          <span>{t.c.engine}: {r.engine_version}</span>{r.data_version && <span>{t.c.data}: {r.data_version}</span>}
          <span>ID: {analysis.id}</span>
        </div>
      </div>
    </section>
  );
};
