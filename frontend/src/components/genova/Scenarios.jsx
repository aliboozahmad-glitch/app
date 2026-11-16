import { Info } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";

export const Scenarios = ({ details }) => {
  const { t } = useLang();
  const pop = details.population_estimate;
  return (
    <div className="space-y-4" data-testid="carrier-scenarios">
      {pop && !pop.available && (
        <div className="flex gap-3 p-4 bg-violet-50 border border-violet-200 rounded-md text-sm text-violet-900" data-testid="population-unavailable">
          <Info size={18} className="shrink-0 mt-0.5" />
          <span><strong>{t.c.popUnavailable}.</strong> {details.region_label ? `(${details.region_label})` : ""}</span>
        </div>
      )}
      <h3 className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500">{t.c.scenarios}</h3>
      <div className="grid md:grid-cols-2 gap-4">
        {details.scenarios.map((s, i) => (
          <div key={i} className="border border-slate-200 rounded-md p-4" data-testid={`scenario-${i}`}>
            <div className="text-sm text-slate-600 mb-3">
              {t.c.ifMother} <span className="font-mono-genes font-semibold text-slate-900">{s.mother_genotype}</span>{" "}
              {t.c.ifFather} <span className="font-mono-genes font-semibold text-slate-900">{s.father_genotype}</span>
            </div>
            <ul className="space-y-1 text-sm">
              {s.outcomes.map((o) => (
                <li key={`${o.group}-${o.key}`} className="flex justify-between gap-3">
                  <span>{o.group !== "all_children" && <span className="text-slate-500">{o.group_label}: </span>}{o.label}</span>
                  <span className="font-mono-genes font-semibold">{o.fraction}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
