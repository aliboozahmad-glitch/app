import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";
import { Trash2, ArrowLeft } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { useApi } from "@/lib/api";
import { CertaintyBadge } from "@/components/genova/primitives";
import { ResultView } from "@/components/genova/ResultView";

export function HistoryPage() {
  const { t, lang } = useLang();
  const api = useApi();
  const [items, setItems] = useState(null);
  const load = useCallback(() => api("get", `/analyses?lang=${lang}`).then((d) => setItems(d.items)), [api, lang]);
  useEffect(() => { load().catch(() => setItems([])); }, [load]);

  const remove = async (id) => {
    await api("delete", `/analyses/${id}`);
    toast.success(t.c.delete);
    load();
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
              <div className="text-xs text-slate-500 font-mono-genes">{new Date(it.created_at).toLocaleString(lang)}</div>
            </div>
            <CertaintyBadge tier={it.certainty} label={it.certainty_label} testId={`history-tier-${it.id}`} />
            <Link to={`/history/${it.id}`} className="text-sm underline underline-offset-2" data-testid={`history-open-${it.id}`}>{t.c.open}</Link>
            <button onClick={() => remove(it.id)} className="text-slate-400 hover:text-red-700 p-1" aria-label={t.c.delete} data-testid={`history-delete-${it.id}`}><Trash2 size={16} /></button>
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
  const [missing, setMissing] = useState(false);
  useEffect(() => { api("get", `/analyses/${id}?lang=${lang}`).then(setAnalysis).catch(() => setMissing(true)); }, [api, id, lang]);
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-8 py-10 space-y-6">
      <Link to="/history" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900" data-testid="back-to-history">
        <ArrowLeft size={14} className="rtl:rotate-180" /> {t.history.title}
      </Link>
      {missing && <p className="text-slate-500" data-testid="analysis-not-found">404</p>}
      {analysis && <><h1 className="text-3xl font-bold tracking-tight">{t.calc[analysis.analysis_type]?.[0]}</h1><ResultView analysis={analysis} /></>}
    </div>
  );
}
