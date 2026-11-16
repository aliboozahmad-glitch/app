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

const SourceText = ({ details }) => {
  const { t } = useLang();
  const kids = (list) => familyNames(list, t);
  if (!details.effective_case) return t.report.notInTable;
  const src = details.source_case;
  const base = details.answer_borrowed
    ? `${t.family.borrowed} #${src.case} (${t.family.wifeShort}: ${kids(src.wife)} · ${t.family.husbandShort}: ${kids(src.husband)})`
    : `${t.family.caseLabel} #${details.effective_case}`;
  return details.origin === "old_app_only" ? `${base} · ${t.family.oldAppOnly}` : base;
};

export const FamilyPatternReport = ({ analysis }) => {
  const { t, lang } = useLang();
  const r = analysis.result;
  const req = analysis.request || r.inputs;
  const d = r.details || {};
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
        <Row label={t.report.number} testId="report-number">{analysis.id}</Row>
        <Row label={t.report.date} testId="report-date">{date}</Row>
        <Row label={t.family.wife} testId="report-wife">{kids(req.wife)}</Row>
        <Row label={t.family.husband} testId="report-husband">{kids(req.husband)}</Row>
        <Row label={t.report.answer} testId="report-answer">{answer ? `${answer.group_label}: ${answer.label}` : "—"}</Row>
        <Row label={t.report.source} testId="report-source"><SourceText details={d} /></Row>
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
SourceText.propTypes = { details: PropTypes.object.isRequired };
