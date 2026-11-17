import { Link } from "react-router-dom";
import { ArrowUpRight, Grid3x3, Droplet, ShieldAlert, Ruler, Eye, Baby, Users } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { CertaintyBadge, Disclaimer } from "@/components/genova/primitives";

const CALCS = [
  ["family-pattern", Users, "traditional_belief"],
  ["mendelian", Grid3x3, "established"], ["blood-type", Droplet, "established"], ["carrier-risk", ShieldAlert, "established"],
  ["height", Ruler, "statistical_estimate"], ["pigmentation", Eye, "uncertain_estimate"], ["sex-ratio", Baby, "population_statistic"],
];
const TIER_KEYS = ["established", "population_estimate", "statistical_estimate", "uncertain_estimate", "population_statistic", "traditional_belief"];
const TIER_NAMES = {
  en: ["Established", "Population estimate", "Statistical estimate", "Uncertain estimate", "Population statistic", "GENOVA Smart Algorithm"],
  ar: ["مُثبت", "تقدير سكاني", "تقدير إحصائي", "تقدير غير مؤكد", "إحصاء سكاني", "خوارزمية GENOVA الذكية"],
  de: ["Gesichert", "Bevölkerungsschätzung", "Statistische Schätzung", "Unsichere Schätzung", "Bevölkerungsstatistik", "GENOVA Smart-Algorithmus"],
};

export const TierLegend = () => {
  const { t, lang } = useLang();
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="tier-legend">
      {TIER_KEYS.map((k, i) => (
        <div key={k} className="bg-white border border-slate-200 rounded-md p-4 space-y-2">
          <CertaintyBadge tier={k} label={TIER_NAMES[lang][i]} testId={`tier-legend-${k}`} />
          <p className="text-xs text-slate-600">{t.tier[k]}</p>
        </div>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const { t, lang } = useLang();
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 py-10 space-y-10">
      <div className="rise">
        <div className="text-xs uppercase tracking-[0.2em] font-semibold text-slate-500">{t.dash.overline}</div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mt-2" data-testid="dashboard-title">{t.dash.title}</h1>
        <p className="text-slate-600 mt-3 max-w-2xl">{t.dash.subtitle}</p>
      </div>
      <Disclaimer text={t.disclaimer} />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CALCS.map(([kind, Icon, tier], i) => (
          <Link key={kind} to={`/calc/${kind}`} data-testid={`calculator-card-${kind}`}
            className="lift group bg-white border border-slate-200 rounded-md p-6 flex flex-col gap-4 rise" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="flex items-start justify-between">
              <span className="w-10 h-10 grid place-items-center border border-slate-200 rounded-md"><Icon size={20} /></span>
              <ArrowUpRight size={18} className="text-slate-400 group-hover:text-slate-900 rtl:-scale-x-100" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-tight">{t.calc[kind][0]}</h2>
              <p className="text-sm text-slate-600 mt-1">{t.calc[kind][1]}</p>
            </div>
            <div className="mt-auto"><CertaintyBadge tier={tier} label={TIER_NAMES[lang][TIER_KEYS.indexOf(tier)]} testId={`calculator-tier-${kind}`} /></div>
          </Link>
        ))}
      </div>
      <TierLegend />
    </div>
  );
}
