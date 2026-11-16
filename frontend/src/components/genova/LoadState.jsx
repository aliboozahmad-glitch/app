import PropTypes from "prop-types";
import { AlertTriangle, Loader2, RotateCw } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";

/** Loading / error / retry wrapper for public data fetched with usePublic. */
export const LoadState = ({ state, testId, children }) => {
  const { t } = useLang();
  const errorBox = (
      <div className="flex flex-wrap items-center gap-3 p-4 border border-red-200 bg-red-50 text-red-800 rounded-md text-sm" data-testid={`${testId}-error`}>
        <AlertTriangle size={16} /> {t.c.loadError}
        <button type="button" onClick={state.retry} data-testid={`${testId}-retry`}
          className="inline-flex items-center gap-1 px-2.5 py-1 border border-red-300 rounded bg-white hover:bg-red-100 transition-colors">
          <RotateCw size={13} /> {t.c.retry}
        </button>
      </div>
  );
  if (state.error && !state.data) return errorBox;
  if (!state.data) {
    return <div className="flex items-center gap-2 text-sm text-slate-500" data-testid={`${testId}-loading`}><Loader2 size={16} className="animate-spin" /> {t.c.loading}</div>;
  }
  return <>{state.error && errorBox}{children(state.data)}</>;
};

LoadState.propTypes = {
  state: PropTypes.shape({ data: PropTypes.any, error: PropTypes.bool, retry: PropTypes.func.isRequired }).isRequired,
  testId: PropTypes.string.isRequired,
  children: PropTypes.func.isRequired,
};
