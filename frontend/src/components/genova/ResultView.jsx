import PropTypes from "prop-types";
import { ExternalLink } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { analysisShape, noteShape, referenceShape, resultShape } from "@/types";
import { CertaintyBadge } from "./primitives";
import { OutcomeTable } from "./OutcomeTable";
import { PunnettGrid } from "./PunnettGrid";
import { Scenarios } from "./Scenarios";
import { FamilyPatternReport, PrintReportButton } from "./FamilyPatternReport";

const SectionTitle = ({ children }) => (
  <h3 className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-2">{children}</h3>
);

SectionTitle.propTypes = { children: PropTypes.node };

const NoteList = ({ title, items, testId }) => (
  <div data-testid={testId}>
    <SectionTitle>{title}</SectionTitle>
    <ul className="space-y-1.5 text-sm text-slate-700 list-disc ps-5">
      {items.map((i) => <li key={i.key}>{i.text}</li>)}
    </ul>
  </div>
);

NoteList.propTypes = { title: PropTypes.string.isRequired, items: PropTypes.arrayOf(noteShape).isRequired, testId: PropTypes.string.isRequired };

export const Sources = ({ refs }) => {
  const { t } = useLang();
  return (
    <div data-testid="result-references">
      <SectionTitle>{t.c.references}</SectionTitle>
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

Sources.propTypes = { refs: PropTypes.arrayOf(referenceShape).isRequired };

const TableCase = ({ details }) => {
  const { t } = useLang();
  const kids = (list) => list.map((g) => (g === "male" ? t.family.boy : t.family.girl)).join(t.family.sep);
  const src = details.answer_borrowed ? details.source_case : null;
  return (
    <div className="text-sm text-slate-500" data-testid="result-table-case">
      <p className="font-mono-genes" data-testid={src ? "result-answer-source" : undefined}>
        {src ? t.family.borrowed : t.family.caseLabel} #{details.effective_case}
        {src && ` (${t.family.wifeShort}: ${kids(src.wife)} · ${t.family.husbandShort}: ${kids(src.husband)})`}
        {details.origin === "old_app_only" && (
          <span className="ms-2 px-2 py-0.5 text-xs rounded border border-amber-300 bg-amber-50 text-amber-900" data-testid="result-old-app-only">{t.family.oldAppOnly}</span>
        )}
      </p>
    </div>
  );
};

TableCase.propTypes = {
  details: PropTypes.shape({
    effective_case: PropTypes.number.isRequired,
    origin: PropTypes.string,
    answer_borrowed: PropTypes.bool,
    source_case: PropTypes.shape({
      case: PropTypes.number,
      wife: PropTypes.arrayOf(PropTypes.string),
      husband: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
};

const ResultHeader = ({ result }) => {
  const { t } = useLang();
  const d = result.details || {};
  const suffix = d.disease_name ? ` · ${d.disease_name}` : "";
  return (
    <div className="p-6 sm:p-8 border-b border-slate-200 flex flex-wrap items-start gap-3 justify-between">
      <div>
        <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500">{t.c.result}{suffix}</div>
        <p className="mt-1 text-slate-900 font-medium" data-testid="result-method">{t.c.method}: {result.method_label}</p>
        {d.inheritance_label && <p className="text-sm text-slate-500" data-testid="result-inheritance">{d.inheritance_label}</p>}
        {d.effective_case && <TableCase details={d} />}
        {d.mechanism_text && <p className="text-sm text-slate-600 mt-2 max-w-2xl" data-testid="result-mechanism">{d.mechanism_text}</p>}
      </div>
      <CertaintyBadge tier={result.certainty} label={result.certainty_label} />
    </div>
  );
};

ResultHeader.propTypes = { result: resultShape.isRequired };

const ResultData = ({ result }) => {
  const d = result.details || {};
  const showScenarios = Boolean(d.scenarios) && result.method !== "carrier_exact";
  return (
    <>
      {result.outcomes.length > 0 && <OutcomeTable result={result} />}
      {showScenarios && <Scenarios details={d} />}
      {d.grid && <PunnettGrid grid={d.grid} />}
    </>
  );
};

ResultData.propTypes = { result: resultShape.isRequired };

const Versions = ({ result, id }) => {
  const { t } = useLang();
  return (
    <div className="text-xs text-slate-400 font-mono-genes flex flex-wrap gap-4" data-testid="result-versions">
      <span>{t.c.engine}: {result.engine_version}</span>
      {result.data_version && <span>{t.c.data}: {result.data_version}</span>}
      <span>ID: {id}</span>
    </div>
  );
};

Versions.propTypes = { result: resultShape.isRequired, id: PropTypes.string.isRequired };

export const ResultView = ({ analysis }) => {
  const { t } = useLang();
  const r = analysis.result;
  const isFamily = r.analysis_type === "family_pattern";
  return (
    <>
    {isFamily && <FamilyPatternReport analysis={analysis} />}
    <section className="bg-white border border-slate-200 rounded-md shadow-sm rise" data-testid="result-card">
      <ResultHeader result={r} />
      <div className="p-6 sm:p-8 space-y-8">
        {isFamily && <PrintReportButton />}
        <ResultData result={r} />
        <div className="grid md:grid-cols-2 gap-8">
          <NoteList title={t.c.assumptions} items={r.assumptions} testId="result-assumptions" />
          <NoteList title={t.c.limitations} items={r.limitations} testId="result-limitations" />
        </div>
        <Sources refs={r.references} />
        <Versions result={r} id={analysis.id} />
      </div>
    </section>
    </>
  );
};

ResultView.propTypes = { analysis: analysisShape.isRequired };
