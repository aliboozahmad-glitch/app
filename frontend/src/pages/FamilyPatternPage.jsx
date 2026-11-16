import { useState } from "react";
import PropTypes from "prop-types";
import { Minus, Plus } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { Choice, FieldLabel } from "@/components/genova/primitives";

const MAX = 3;

const FamilyInput = ({ id, label, children, onChange }) => {
  const { t } = useLang();
  const options = [["male", t.family.boy], ["female", t.family.girl]];
  const setAt = (i) => (v) => onChange(children.map((c, j) => (j === i ? v : c)));
  return (
    <div className="border border-slate-200 rounded-md p-5 space-y-4" data-testid={`${id}-family`}>
      <FieldLabel>{label}</FieldLabel>
      {children.map((c, i) => (
        // Position is the identity here: children are an ordered birth sequence.
        <div key={`${id}-${i}`} className="flex items-center gap-3">
          <span className="text-sm text-slate-500 w-16">{t.family.child} {i + 1}</span>
          <Choice testId={`${id}-child-${i}`} value={c} onChange={setAt(i)} options={options} />
        </div>
      ))}
      <div className="flex gap-2">
        <button type="button" disabled={children.length >= MAX} onClick={() => onChange([...children, "male"])} data-testid={`${id}-add-child`}
          className="inline-flex items-center gap-1 text-sm px-3 py-1.5 border border-slate-300 rounded-md hover:border-slate-500 disabled:opacity-40 transition-colors">
          <Plus size={14} /> {t.family.add}
        </button>
        <button type="button" disabled={children.length <= 1} onClick={() => onChange(children.slice(0, -1))} data-testid={`${id}-remove-child`}
          className="inline-flex items-center gap-1 text-sm px-3 py-1.5 border border-slate-300 rounded-md hover:border-slate-500 disabled:opacity-40 transition-colors">
          <Minus size={14} /> {t.family.remove}
        </button>
      </div>
    </div>
  );
};

FamilyInput.propTypes = {
  id: PropTypes.oneOf(["wife", "husband"]).isRequired,
  label: PropTypes.string.isRequired,
  children: PropTypes.arrayOf(PropTypes.oneOf(["male", "female"])).isRequired,
  onChange: PropTypes.func.isRequired,
};

export default function FamilyPatternPage() {
  const { t } = useLang();
  const { run, analysis, loading, error } = useAnalysis("family-pattern");
  const [wife, setWife] = useState(["male", "male", "female"]);
  const [husband, setHusband] = useState(["male", "male", "female"]);
  const [childNumber, setChildNumber] = useState("1");
  return (
    <CalcLayout kind="family-pattern" loading={loading} error={error} analysis={analysis}
      onSubmit={() => run({ wife, husband, child_number: Number(childNumber) })}>
      <p className="text-sm text-amber-900 bg-amber-50 border border-amber-200 rounded-md p-4" data-testid="family-pattern-notice">{t.family.notice}</p>
      <div className="grid md:grid-cols-2 gap-6">
        <FamilyInput id="wife" label={t.family.wife} onChange={setWife}>{wife}</FamilyInput>
        <FamilyInput id="husband" label={t.family.husband} onChange={setHusband}>{husband}</FamilyInput>
      </div>
      <div>
        <FieldLabel>{t.family.which}</FieldLabel>
        <Choice testId="child-number" value={childNumber} onChange={setChildNumber} options={[["1", t.family.first], ["2", t.family.second]]} />
      </div>
    </CalcLayout>
  );
}
