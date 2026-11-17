import PropTypes from "prop-types";
import { useLang } from "@/i18n/LanguageContext";
import { outcomeShape, resultShape } from "@/types";
import { pct } from "@/lib/format";

const GROUP_TITLE = "text-xs uppercase tracking-[0.18em] font-semibold text-slate-500";
const RAW_KINDS = ["genotype", "blood_type"];

const Bar = ({ p }) => (
  <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden w-28">
    <div className="h-full bg-slate-900" style={{ width: `${Math.max(p * 100, 1)}%` }} />
  </div>
);

Bar.propTypes = { p: PropTypes.number.isRequired };


const OutcomeValue = ({ o }) => {
  if (o.kind === "measurement") {
    return <span className="font-semibold">{o.value} {o.unit} <span className="text-slate-500">({o.range[0]}–{o.range[1]})</span></span>;
  }
  if (o.fraction) return <span className="font-semibold">{o.fraction} <span className="text-slate-500">· {pct(o.probability)}</span></span>;
  if (o.range_fraction) return <span>{o.range_fraction[0]} – {o.range_fraction[1]}</span>;
  if (o.stated_range) return <bdi dir="ltr" className="font-semibold">{o.stated_range}</bdi>;
  return null;
};

OutcomeValue.propTypes = { o: outcomeShape.isRequired };

const Row = ({ o, i }) => (
  <tr className="border-t border-slate-100" data-testid={`outcome-row-${i}`}>
    <td className="py-2.5 pe-4 text-sm"><span className={RAW_KINDS.includes(o.kind) ? "font-mono-genes font-semibold" : ""}>{o.label}</span></td>
    <td className="py-2.5 pe-4 text-sm font-mono-genes" data-testid={`outcome-value-${i}`}><OutcomeValue o={o} /></td>
    <td className="py-2.5">{o.probability != null && <Bar p={o.probability} />}</td>
  </tr>
);

Row.propTypes = { o: outcomeShape.isRequired, i: PropTypes.number.isRequired };

const groupsOf = (outcomes) => [...new Set(outcomes.map((o) => o.group))].map((g) => {
  const items = outcomes.filter((o) => o.group === g);
  return { id: g, label: items[0].group_label, items };
});

const QualitativeBands = ({ outcomes }) => (
  <div className="grid sm:grid-cols-3 gap-4" data-testid="qualitative-bands">
    {groupsOf(outcomes).map((g) => (
      <div key={g.id} className="border border-slate-200 rounded-md p-4">
        <div className={`${GROUP_TITLE} mb-3`}>{g.label}</div>
        <div className="flex flex-wrap gap-2">
          {g.items.map((o) => <span key={o.key} className="px-2.5 py-1 bg-slate-100 rounded text-sm" data-testid={`band-${g.id}-${o.key}`}>{o.label}</span>)}
        </div>
      </div>
    ))}
  </div>
);

QualitativeBands.propTypes = { outcomes: PropTypes.arrayOf(outcomeShape).isRequired };

const ImpossibleTypes = ({ types }) => {
  const { t } = useLang();
  return (
    <div data-testid="impossible-types">
      <div className={`${GROUP_TITLE} mb-2`}>{t.c.impossible}</div>
      <div className="flex flex-wrap gap-2">
        {types.map((x) => <span key={x} className="font-mono-genes text-sm px-2 py-0.5 border border-dashed border-slate-300 text-slate-400 rounded line-through">{x}</span>)}
      </div>
    </div>
  );
};

ImpossibleTypes.propTypes = { types: PropTypes.arrayOf(PropTypes.string).isRequired };

const GroupTable = ({ group, offset }) => (
  <div>
    <div className={`${GROUP_TITLE} mb-1`}>{group.label}</div>
    <table className="w-full text-start table-fixed">
      <colgroup><col className="w-[50%]" /><col className="w-[30%]" /><col className="w-[20%]" /></colgroup>
      <tbody>{group.items.map((o, j) => <Row key={`${o.kind}-${o.key}`} o={o} i={offset + j} />)}</tbody>
    </table>
  </div>
);

GroupTable.propTypes = {
  group: PropTypes.shape({ id: PropTypes.string, label: PropTypes.string, items: PropTypes.arrayOf(outcomeShape) }).isRequired,
  offset: PropTypes.number.isRequired,
};

export const OutcomeTable = ({ result }) => {
  const { t } = useLang();
  if (result.outcomes.every((o) => o.kind === "qualitative")) return <QualitativeBands outcomes={result.outcomes} />;
  const groups = groupsOf(result.outcomes);
  const offsets = groups.map((_, gi) => groups.slice(0, gi).reduce((n, g) => n + g.items.length, 0));
  const impossible = result.details?.impossible_types || [];
  return (
    <div className="space-y-6" data-testid="outcome-table">
      {result.details?.exact === false && <p className="text-sm text-slate-600">{t.c.range}</p>}
      {groups.map((g, gi) => <GroupTable key={g.id} group={g} offset={offsets[gi]} />)}
      {impossible.length > 0 && <ImpossibleTypes types={impossible} />}
    </div>
  );
};

OutcomeTable.propTypes = { result: resultShape.isRequired };
