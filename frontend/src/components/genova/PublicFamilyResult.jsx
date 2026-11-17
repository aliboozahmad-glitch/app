import PropTypes from "prop-types";
import { createPortal } from "react-dom";
import { useLang } from "@/i18n/LanguageContext";
import { analysisShape } from "@/types";
import { PrintReportButton } from "./FamilyPatternReport";
import { ResultFeedback } from "./ResultFeedback";

const PublicContent = ({ analysis, testPrefix }) => {
  const { t, lang } = useLang();
  const r = analysis.result;
  const o = r.outcomes[0];
  const date = analysis.created_at ? new Date(analysis.created_at).toLocaleDateString(lang) : "";
  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between gap-4 flex-wrap">
        <div className="text-lg font-bold tracking-tight">GENOVA<span className="text-slate-400">AI</span></div>
        <div className="text-xs text-slate-500 font-mono-genes">
          <span data-testid={`${testPrefix}-date`}>{date}</span> · <span data-testid={`${testPrefix}-id`}>{analysis.report_id}</span>
        </div>
      </div>
      <div>
        <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500">{o ? o.group_label : t.c.result}</div>
        <div className="text-4xl font-bold mt-1" data-testid={`${testPrefix}-answer`}>{o ? o.label : "—"}</div>
        {o?.stated_range && <p className="mt-2 text-slate-700" data-testid={`${testPrefix}-range`}>{t.report.range}: <bdi dir="ltr">{o.stated_range}</bdi></p>}
      </div>
      <div className="text-sm text-slate-600 space-y-1" data-testid={`${testPrefix}-disclaimer`}>
        {r.limitations.map((l) => <p key={l.key}>{l.text}</p>)}
      </div>
    </div>
  );
};

PublicContent.propTypes = { analysis: analysisShape.isRequired, testPrefix: PropTypes.string.isRequired };

export const PublicFamilyResult = ({ analysis }) => {
  const { lang } = useLang();
  return (
    <>
      {createPortal(
        <article className="print-report" dir={lang === "ar" ? "rtl" : "ltr"} data-testid="family-pattern-report">
          <PublicContent analysis={analysis} testPrefix="report" />
        </article>,
        document.body,
      )}
      <section className="bg-white border border-slate-200 rounded-md shadow-sm rise p-6 sm:p-8 space-y-6" data-testid="result-card">
        <PublicContent analysis={analysis} testPrefix="public-result" />
        <PrintReportButton />
        <ResultFeedback analysisId={analysis.id} />
      </section>
    </>
  );
};

PublicFamilyResult.propTypes = { analysis: analysisShape.isRequired };
