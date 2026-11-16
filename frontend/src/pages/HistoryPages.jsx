import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";
import { Trash2, ArrowLeft } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { errorMessage, useApi } from "@/lib/api";
import { summarize } from "@/lib/format";

import { CertaintyBadge } from "@/components/genova/primitives";
import { ResultView } from "@/components/genova/ResultView";

export function HistoryPage() {
  const { t, lang } = useLang();
  const api = useApi();
  const [items, setItems] = useState(null);
  const [pending, setPending] = useState(null);
  const load = useCallback(() => api("get", `/analyses?lang=${lang}`).then((d) => setItems(d.items)), [api, lang]);
  useEffect(() => { load().catch(() => setItems([])); }, [load]);

  const remove = async (id) => {
    if (pending !== id) return setPending(id);
    setPending(null);
    try {
      await api("delete", `/analyses/${id}`);
      toast.success(t.c.deleted);
      await load();
    } catch (e) {
      toast.error(errorMessage(e, t.c.error));
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-8 py-10 space-y-8">
      <div>
        <div className="text-xs uppercase tracking-[0.2em] font-semibold text-slate-500">{t.history.overline}</div>
        <h1 className="text-4xl font-bold tracking-tight mt-2" data-testid="history-title">{t.history.title}</h1>
      </div>
      {items && items.length === 0 && <p className="text-slate-500" data-testid="history-empty">{t.c.empty}</p>}
      <ul className="bg-white border border-slate-200 rounded-md divide-y divide-slate-100" data-testid="history-list">
        {items?.map((it) => (
          <li key={it.id} className="p-4 sm:p-5 flex flex-wrap items-center gap-3" data-testid={`history-item-${it.id}`}>
            <div className="flex-1 min-w-[220px]">
              <div className="font-medium">{t.calc[it.analysis_type]?.[0]}{it.disease_name ? ` · ${it.disease_name}` : ""}</div>
              <div className="text-sm text-slate-600 font-mono-genes" data-testid={`history-summary-${it.id}`}>{summarize(it)}</div>
              <div className="text-xs text-slate-500 font-mono-genes">{new Date(it.created_at).toLocaleString(lang)}</div>
            </div>
            <CertaintyBadge tier={it.certainty} label={it.certainty_label} testId={`history-tier-${it.id}`} />
            <Link to={`/history/${it.id}`} className="text-sm underline underline-offset-2" data-testid={`history-open-${it.id}`}>{t.c.open}</Link>
            <button onClick={() => remove(it.id)} aria-label={t.c.delete} data-testid={`history-delete-${it.id}`}
              className={`text-xs inline-flex items-center gap-1 px-2 py-1 rounded border transition-colors ${pending === it.id ? "border-red-300 bg-red-50 text-red-700" : "border-transparent text-slate-400 hover:text-red-700"}`}>
              <Trash2 size={14} />{pending === it.id && t.c.confirmDelete}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function AnalysisDetailPage() {
  const { id } = useParams();
  const { t, lang } = useLang();
  const api = useApi();
  const [analysis, setAnalysis] = useState(null);
  const [failure, setFailure] = useState(null);
  useEffect(() => {
    api("get", `/analyses/${id}?lang=${lang}`).then(setAnalysis)
      .catch((e) => setFailure(e?.response?.status === 404 ? t.c.notFound : errorMessage(e, t.c.error)));
  }, [api, id, lang, t]);
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-8 py-10 space-y-6">
      <Link to="/history" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900" data-testid="back-to-history">
        <ArrowLeft size={14} className="rtl:rotate-180" /> {t.history.title}
      </Link>
      {failure && <p className="text-slate-500" data-testid="analysis-error">{failure}</p>}
      {analysis && <><h1 className="text-3xl font-bold tracking-tight">{t.calc[analysis.analysis_type]?.[0]}</h1><ResultView analysis={analysis} /></>}
    </div>
  );
}
