import PropTypes from "prop-types";
import { useLang } from "@/i18n/LanguageContext";
import { useAuthedGet } from "@/lib/api";
import { LoadState } from "@/components/genova/LoadState";

const pct = (v) => (v === null || v === undefined ? "—" : `${v}%`);

const Stat = ({ label, value, testId }) => (
  <div className="border border-slate-200 rounded-md p-4 bg-white">
    <div className="text-xs uppercase tracking-[0.14em] text-slate-500 font-semibold">{label}</div>
    <div className="text-2xl font-bold mt-1 font-mono-genes" data-testid={testId}>{value}</div>
  </div>
);

Stat.propTypes = { label: PropTypes.string.isRequired, value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired, testId: PropTypes.string };

const RateTable = ({ title, rows, nameOf, testId }) => {
  const { t } = useLang();
  return (
    <div>
      <h4 className="text-sm font-semibold mb-2">{title}</h4>
      <table className="w-full text-sm border border-slate-200 bg-white" data-testid={testId}>
        <thead className="bg-slate-50 text-slate-600">
          <tr>{[t.stats.group, t.stats.confirmed, t.stats.matches, t.stats.mismatches, t.stats.matchRate].map((h) => <th key={h} className="text-start p-2">{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.range ?? r.method ?? "none"} className="border-t border-slate-200">
              <td className="p-2">{nameOf(r)}</td><td className="p-2">{r.confirmed}</td><td className="p-2">{r.matches}</td>
              <td className="p-2">{r.mismatches}</td><td className="p-2">{pct(r.match_rate)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

RateTable.propTypes = { title: PropTypes.string.isRequired, rows: PropTypes.array.isRequired, nameOf: PropTypes.func.isRequired, testId: PropTypes.string };

const StageStats = ({ stage, s }) => {
  const { t } = useLang();
  return (
    <section className="space-y-4" data-testid={`stats-stage-${stage}`}>
      <h3 className="text-lg font-semibold">{t.feedback.stages[stage]}</h3>
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <Stat label={t.stats.confirmed} value={s.confirmed} testId={`stats-${stage}-confirmed`} />
        <Stat label={t.family.boy} value={s.actual.male} testId={`stats-${stage}-boys`} />
        <Stat label={t.family.girl} value={s.actual.female} testId={`stats-${stage}-girls`} />
        <Stat label={t.stats.matches} value={s.matches} testId={`stats-${stage}-matches`} />
        <Stat label={t.stats.mismatches} value={s.mismatches} testId={`stats-${stage}-mismatches`} />
        <Stat label={t.stats.matchRate} value={pct(s.match_rate)} testId={`stats-${stage}-rate`} />
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <RateTable title={t.stats.byRange} rows={s.by_range} nameOf={(r) => (r.range ? <bdi dir="ltr">{r.range}</bdi> : t.stats.noRange)} testId={`stats-${stage}-by-range`} />
        <RateTable title={t.stats.byMethod} rows={s.by_method} nameOf={(r) => t.stats.methods[r.method]} testId={`stats-${stage}-by-method`} />
      </div>
    </section>
  );
};

StageStats.propTypes = { stage: PropTypes.string.isRequired, s: PropTypes.object.isRequired };

const Ratings = ({ r }) => {
  const { t } = useLang();
  return (
    <section className="space-y-4" data-testid="stats-ratings">
      <h3 className="text-lg font-semibold">{t.stats.ratingsTitle}</h3>
      <p className="text-xs text-slate-500">{t.stats.ratingsNote}</p>
      <div className="grid grid-cols-3 gap-3">
        <Stat label={t.feedback.like} value={r.likes} testId="stats-likes" />
        <Stat label={t.feedback.dislike} value={r.dislikes} testId="stats-dislikes" />
        <Stat label={t.stats.satisfaction} value={pct(r.satisfaction)} testId="stats-satisfaction" />
      </div>
      <table className="w-full text-sm border border-slate-200 bg-white" data-testid="stats-ratings-by-type">
        <thead className="bg-slate-50 text-slate-600">
          <tr>{[t.stats.calculator, t.feedback.like, t.feedback.dislike, t.stats.satisfaction].map((h) => <th key={h} className="text-start p-2">{h}</th>)}</tr>
        </thead>
        <tbody>
          {r.by_type.map((x) => (
            <tr key={x.analysis_type} className="border-t border-slate-200">
              <td className="p-2">{t.calc[x.analysis_type]?.[0] || x.analysis_type}</td><td className="p-2">{x.likes}</td>
              <td className="p-2">{x.dislikes}</td><td className="p-2">{pct(x.satisfaction)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};

Ratings.propTypes = { r: PropTypes.object.isRequired };

const Limits = ({ l }) => {
  const { t } = useLang();
  return (
    <section className="space-y-4" data-testid="stats-limits">
      <h3 className="text-lg font-semibold">{t.stats.limitsTitle}</h3>
      <p className="text-xs text-slate-500">{t.stats.limitsNote.replace("{days}", l.days).replace("{account}", l.account_limit).replace("{network}", l.network_limit)}</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label={t.stats.accountBlocked} value={l.accounts.blocked_attempts} testId="stats-account-blocked" />
        <Stat label={t.stats.accountHits} value={l.accounts.limit_hits} testId="stats-account-hits" />
        <Stat label={t.stats.networkBlocked} value={l.networks.blocked_attempts} testId="stats-network-blocked" />
        <Stat label={t.stats.networkHits} value={l.networks.limit_hits} testId="stats-network-hits" />
      </div>
    </section>
  );
};

Limits.propTypes = { l: PropTypes.object.isRequired };

export default function AdminStatsPage() {
  const { t } = useLang();
  const state = useAuthedGet("/admin/stats");
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 space-y-10" data-testid="admin-stats-page">
      {state.forbidden ? <p className="text-sm text-slate-600" data-testid="stats-forbidden">{t.stats.forbidden}</p> : (
      <>
      <header>
        <h1 className="text-4xl sm:text-5xl font-display font-extrabold tracking-tight">{t.stats.title}</h1>
        <p className="mt-3 text-sm text-amber-900 bg-amber-50 border border-amber-200 rounded-md p-3" data-testid="stats-observational-label">{t.stats.label}</p>
      </header>
      <LoadState state={state} testId="admin-stats">
        {(data) => (
          <>
            <div className="grid grid-cols-2 gap-3 max-w-xl">
              <Stat label={t.stats.predictions} value={data.predictions_total} testId="stats-predictions-total" />
              <Stat label={t.stats.confirmedTotal} value={data.confirmed_total} testId="stats-confirmed-total" />
            </div>
            <StageStats stage="pregnancy" s={data.stages.pregnancy} />
            <StageStats stage="birth" s={data.stages.birth} />
            <Ratings r={data.ratings} />
            <Limits l={data.limits} />
          </>
        )}
      </LoadState>
      </>
      )}
    </div>
  );
}
