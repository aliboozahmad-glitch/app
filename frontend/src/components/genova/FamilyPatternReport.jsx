import PropTypes from "prop-types";
import { createPortal } from "react-dom";
import { Printer } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { familyNames } from "@/lib/format";
import { analysisShape } from "@/types";

const Row = ({ label, children, testId }) => (
  <div className="flex gap-4 py-2 border-b border-slate-200">
    <dt className="w-48 shrink-0 text-slate-500">{label}</dt>
    <dd className="font-medium text-slate-900" data-testid={testId}>{children}</dd>
  </div>
);

Row.propTypes = { label: PropTypes.string.isRequired, children: PropTypes.node, testId: PropTypes.string };

export const PrintReportButton = () => {
  const { t } = useLang();
  return (
    <button type="button" onClick={() => window.print()} data-testid="print-report-button"
      className="no-print inline-flex items-center gap-2 text-sm px-4 py-2 border border-slate-300 rounded-md hover:border-slate-500 transition-colors">
      <Printer size={16} /> {t.report.print}
    </button>
  );
};

const FamilyPercentageBar = ({ outcome, t }) => {
  if (outcome?.probability == null || !["male", "female"].includes(outcome.key)) return null;
  const expected = Math.round(outcome.probability * 100);
  const male = outcome.key === "male" ? expected : 100 - expected;
  const female = 100 - male;
  return (
    <div className="my-4 space-y-2" data-testid="family-percentage-bar">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100" role="img"
        aria-label={t.family.boy + " " + male + "%, " + t.family.girl + " " + female + "%"}>
        <div className="h-full bg-blue-500" style={{ width: male + "%" }} />
        <div className="h-full bg-pink-400" style={{ width: female + "%" }} />
      </div>
      <div className="flex justify-between gap-2 text-sm">
        <span className="text-blue-700">{t.family.boy}: <bdi dir="ltr">{male}%</bdi></span>
        <span className="text-pink-700">{t.family.girl}: <bdi dir="ltr">{female}%</bdi></span>
      </div>
      <p className="text-xs text-slate-500">{t.family.percentageNote}</p>
    </div>
  );
};
export const FamilyPatternReport = ({ analysis }) => {
  const { t, lang } = useLang();
  const r = analysis.result;
  const req = analysis.request || r.inputs;
  const kids = (list) => familyNames(list, t);
  const answer = r.outcomes[0];
  const date = analysis.created_at ? new Date(analysis.created_at).toLocaleString(lang) : "";
  return createPortal(
    <article className="print-report text-sm" dir={lang === "ar" ? "rtl" : "ltr"} data-testid="family-pattern-report">
      <header className="mb-6">
        <div className="text-lg font-bold">GENOVA AI</div>
        <h1 className="text-2xl font-bold">{t.report.title}</h1>
        <p className="mt-2 font-semibold" data-testid="report-traditional-note">{r.certainty_label}</p>
      </header>
      <dl className="mb-6">
        <Row label={t.report.number} testId="report-number">{analysis.report_id || analysis.id}</Row>
        <Row label={t.report.date} testId="report-date">{date}</Row>
        <Row label={t.family.wife} testId="report-wife">{kids(req.wife)}</Row>
        <Row label={t.family.husband} testId="report-husband">{kids(req.husband)}</Row>
        <Row label={t.report.answer} testId="report-answer">{answer ? `${answer.group_label}: ${answer.label}${answer.stated_range ? ` (${answer.stated_range})` : ""}` : "—"}</Row>
        {answer?.probability != null && <Row label={t.family.percentageNote} testId="report-percentage"><FamilyPercentageBar outcome={answer} t={t} /></Row>}
      </dl>
      <p className="mb-4">{t.family.notice}</p>
      <h2 className="font-semibold mb-2">{t.c.limitations}</h2>
      <ul className="list-disc ps-5 space-y-1 mb-6" data-testid="report-notes">
        {r.limitations.map((l) => <li key={l.key}>{l.text}</li>)}
      </ul>
      <p className="text-xs text-slate-600">{t.disclaimer}</p>
      <p className="text-xs text-slate-500 mt-2">{r.engine_version} · {r.data_version}</p>
    </article>,
    document.body,
  );
};

FamilyPatternReport.propTypes = { analysis: analysisShape.isRequired };
