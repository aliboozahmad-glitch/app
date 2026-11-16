import PropTypes from "prop-types";
import { analysisShape } from "@/types";
import { Link } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { Disclaimer } from "./primitives";
import { ResultView } from "./ResultView";

export const CalcLayout = ({ kind, onSubmit, loading, error, analysis, children, disabled = false }) => {
  const { t } = useLang();
  const [title, desc] = t.calc[kind];
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-8 py-10 space-y-8">
      <Link to="/dashboard" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900" data-testid="back-to-dashboard">
        <ArrowLeft size={14} className="rtl:rotate-180" /> {t.c.back}
      </Link>
      <div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight" data-testid="calculator-title">{title}</h1>
        <p className="text-slate-600 mt-2">{desc}</p>
      </div>
      <Disclaimer text={t.disclaimer} />
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}
        className="bg-white border border-slate-200 rounded-md shadow-sm p-6 sm:p-8 space-y-6" data-testid="calculator-form">
        {children}
        <div className="flex items-center gap-4">
          <button type="submit" disabled={loading || disabled} data-testid="calculate-button"
            className="inline-flex items-center gap-2 bg-slate-900 text-white px-6 py-2.5 rounded-md font-medium hover:bg-slate-800 disabled:opacity-60 transition-colors">
            {loading && <Loader2 size={16} className="animate-spin" />}{loading ? t.c.calculating : t.c.calculate}
          </button>
          {analysis && <span className="text-xs text-slate-500" data-testid="saved-indicator">{t.c.saved}</span>}
        </div>
        {error && <p className="text-sm text-red-700" data-testid="calculator-error">{error}</p>}
      </form>
      {analysis && <ResultView analysis={analysis} />}
    </div>
  );
};

CalcLayout.propTypes = {
  kind: PropTypes.oneOf(["mendelian", "blood-type", "carrier-risk", "height", "pigmentation", "sex-ratio"]).isRequired,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  error: PropTypes.string,
  analysis: analysisShape,
  children: PropTypes.node,
  disabled: PropTypes.bool,
};
