import { useLang } from "@/i18n/LanguageContext";

const Bar = ({ p }) => (
  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden w-28">
    <div className="h-full bg-slate-900" style={{ width: `${Math.max(p * 100, 1)}%` }} />
  </div>
);

const pct = (p) => `${(p * 100).toFixed(p * 100 % 1 === 0 ? 0 : 2)}%`;

const Row = ({ o, i }) => (
  <tr className="border-t border-slate-100" data-testid={`outcome-row-${i}`}>
    <td className="py-2.5 pe-4 text-sm">
      <span className={o.kind === "genotype" || o.kind === "blood_type" ? "font-mono-genes font-semibold" : ""}>{o.label}</span>
    </td>
    <td className="py-2.5 pe-4 text-sm font-mono-genes" data-testid={`outcome-value-${i}`}>
      {o.kind === "measurement" && <span className="font-semibold">{o.value} {o.unit} <span className="text-slate-500">({o.range[0]}–{o.range[1]})</span></span>}
      {o.fraction && <span className="font-semibold">{o.fraction} <span className="text-slate-500">· {pct(o.probability)}</span></span>}
      {o.range_fraction && <span>{o.range_fraction[0]} – {o.range_fraction[1]}</span>}
    </td>
    <td className="py-2.5">{o.probability != null && <Bar p={o.probability} />}</td>
  </tr>
);

export const OutcomeTable = ({ result }) => {
  const { t } = useLang();
  const groups = [...new Set(result.outcomes.map((o) => o.group))];
  const qualitative = result.outcomes.every((o) => o.kind === "qualitative");
  if (qualitative) {
    return (
      <div className="grid sm:grid-cols-3 gap-4" data-testid="qualitative-bands">
        {groups.map((g) => (
          <div key={g} className="border border-slate-200 rounded-md p-4">
            <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-3">{result.outcomes.find((o) => o.group === g).group_label}</div>
            <div className="flex flex-wrap gap-2">
              {result.outcomes.filter((o) => o.group === g).map((o) => (
                <span key={o.key} className="px-2.5 py-1 bg-slate-100 rounded text-sm" data-testid={`band-${g}-${o.key}`}>{o.label}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }
  let idx = 0;
  return (
    <div className="space-y-6" data-testid="outcome-table">
      {result.details?.exact === false && <p className="text-sm text-slate-600">{t.c.range}</p>}
      {groups.map((g) => (
        <div key={g}>
          <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-1">{result.outcomes.find((o) => o.group === g).group_label}</div>
          <table className="w-full text-start">
            <tbody>{result.outcomes.filter((o) => o.group === g).map((o) => <Row key={`${o.kind}-${o.key}`} o={o} i={idx++} />)}</tbody>
          </table>
        </div>
      ))}
      {result.details?.impossible_types?.length > 0 && (
        <div data-testid="impossible-types">
          <div className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-2">{t.c.impossible}</div>
          <div className="flex flex-wrap gap-2">
            {result.details.impossible_types.map((x) => <span key={x} className="font-mono-genes text-sm px-2 py-0.5 border border-dashed border-slate-300 text-slate-400 rounded line-through">{x}</span>)}
          </div>
        </div>
      )}
    </div>
  );
};
