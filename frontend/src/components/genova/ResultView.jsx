import PropTypes from "prop-types";
import { ExternalLink } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { analysisShape, noteShape, referenceShape, resultShape } from "@/types";
import { CertaintyBadge } from "./primitives";
import { OutcomeTable } from "./OutcomeTable";
import { PunnettGrid } from "./PunnettGrid";
import { Scenarios } from "./Scenarios";
import { FamilyPatternReport, PrintReportButton } from "./FamilyPatternReport";
import { PublicFamilyResult } from "./PublicFamilyResult";
import { ResultFeedback } from "./ResultFeedback";

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
              {r.url ? (
                <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-slate-900 underline underline-offset-2 hover:text-slate-600" data-testid={`reference-link-${r.id}`}>
                  {r.title}<ExternalLink size={12} className="inline ms-1" />
                </a>
              ) : <span className="text-slate-900" data-testid={`reference-link-${r.id}`}>{r.title}</span>}
              {r.url && <span className="text-slate-500"> · {r.publisher} · {r.link_check === "verified_2026_06" ? t.c.verified : t.c.manual}</span>}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
};

Sources.propTypes = { refs: PropTypes.arrayOf(referenceShape).isRequired };

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
        {d.mechanism_text && <p className="text-sm text-slate-600 mt-2 max-w-2xl" data-testid="result-mechanism">{d.mechanism_text}</p>}
      </div>
      <CertaintyBadge tier={result.certainty} label={result.certainty_label} />
    </div>
  );
};

ResultHeader.propTypes = { result: resultShape.isRequired };

const FamilyPercentageBar = ({ outcome }) => {
  const { t } = useLang();
  if (outcome.probability == null || !["male", "female"].includes(outcome.key)) return null;
  const expected = Math.round(outcome.probability * 100);
  const male = outcome.key === "male" ? expected : 100 - expected;
  const female = 100 - male;
  return (
    <div className="mt-4 space-y-2" data-testid="family-percentage-bar">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100" role="img"
        aria-label={t.family.boy + " " + male + "%, " + t.family.girl + " " + female + "%"}>
        <div className="h-full bg-blue-500" style={{ width: male + "%" }} />
        <div className="h-full bg-pink-400" style={{ width: female + "%" }} />
      </div>
      <div className="flex flex-wrap justify-between gap-2 text-sm">
        <span className="text-blue-700">{t.family.boy}: <bdi dir="ltr">{male}%</bdi></span>
        <span className="text-pink-700">{t.family.girl}: <bdi dir="ltr">{female}%</bdi></span>
      </div>
      <p className="text-xs text-slate-500">{t.family.percentageNote}</p>
    </div>
  );
};

FamilyPercentageBar.propTypes = { outcome: PropTypes.object.isRequired };

const FamilyAnswer = ({ result }) => {
  const { t } = useLang();
  const o = result.outcomes[0];
  if (!o) return <p className="text-2xl font-bold" data-testid="family-no-match">{t.report.notInTable}</p>;
  return (
    <div>
      <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500">{o.group_label}</div>
      <div className="text-4xl font-bold mt-1" data-testid="family-answer">{o.label}</div>
      <FamilyPercentageBar outcome={o} />
      {!o.probability && o.stated_range && <p className="mt-2 text-slate-700" data-testid="family-range">{t.report.range}: <bdi dir="ltr">{o.stated_range}</bdi></p>}
    </div>
  );
};

FamilyAnswer.propTypes = { result: resultShape.isRequired };

const ResultData = ({ result }) => {
  const d = result.details || {};
  const showScenarios = Boolean(d.scenarios) && result.method !== "carrier_exact";
  if (result.analysis_type === "family_pattern") return <FamilyAnswer result={result} />;
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
  if (r.public) return <PublicFamilyResult analysis={analysis} />;
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
        <ResultFeedback analysisId={analysis.id} />
      </div>
    </section>
    </>
  );
};

ResultView.propTypes = { analysis: analysisShape.isRequired };
