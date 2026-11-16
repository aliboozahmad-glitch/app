import PropTypes from "prop-types";
import { TIERS } from "@/types";
import { ShieldCheck, BarChart3, Users, HelpCircle, Globe2, ScrollText } from "lucide-react";

export const TIER_STYLE = {
  established: ["bg-emerald-50 text-emerald-800 border-emerald-200", ShieldCheck],
  population_estimate: ["bg-violet-50 text-violet-800 border-violet-200", Users],
  statistical_estimate: ["bg-blue-50 text-blue-800 border-blue-200", BarChart3],
  uncertain_estimate: ["bg-amber-50 text-amber-800 border-amber-200", HelpCircle],
  population_statistic: ["bg-slate-100 text-slate-700 border-slate-300", Globe2],
  traditional_belief: ["bg-orange-50 text-orange-800 border-orange-300 border-dashed", ScrollText],
};

export const CertaintyBadge = ({ tier, label, testId = "certainty-badge" }) => {
  const [cls, Icon] = TIER_STYLE[tier] || TIER_STYLE.population_statistic;
  return (
    <span data-testid={testId} data-tier={tier}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      <Icon size={13} /> {label}
    </span>
  );
};

export const Disclaimer = ({ text }) => (
  <div data-testid="disclaimer-banner" className="bg-slate-100 border-s-4 border-slate-500 p-4 text-sm text-slate-700 rounded-e-md">
    {text}
  </div>
);

export const Choice = ({ options, value, onChange, testId }) => (
  <div className="flex flex-wrap gap-2" data-testid={testId}>
    {options.map(([v, label]) => (
      <button type="button" key={v} onClick={() => onChange(v)} data-testid={`${testId}-${v}`}
        className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${value === v ? "bg-slate-900 text-white border-slate-900" : "bg-white text-slate-700 border-slate-300 hover:border-slate-500"}`}>
        {label}
      </button>
    ))}
  </div>
);

export const FieldLabel = ({ children }) => (
  <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-2">{children}</div>
);

CertaintyBadge.propTypes = { tier: PropTypes.oneOf(TIERS).isRequired, label: PropTypes.string.isRequired, testId: PropTypes.string };
Disclaimer.propTypes = { text: PropTypes.string.isRequired };
Choice.propTypes = {
  options: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.node)).isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  testId: PropTypes.string.isRequired,
};
FieldLabel.propTypes = { children: PropTypes.node };
