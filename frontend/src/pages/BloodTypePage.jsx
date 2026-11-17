import PropTypes from "prop-types";
import { useState } from "react";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { Choice, FieldLabel } from "@/components/genova/primitives";

const ABO = { type: ["A", "B", "AB", "O"], genotype: ["AA", "AO", "BB", "BO", "AB", "OO"] };
const RH = { type: ["+", "-"], genotype: ["DD", "Dd", "dd"] };

const ParentInput = ({ id, label, state, setState }) => {
  const { t } = useLang();
  const set = (k) => (v) => setState({ ...state, [k]: v });
  const switchMode = (m) => setState({ mode: m, abo: ABO[m][0], rh: RH[m][0] });
  const mono = (l) => l.map((v) => [v, <span key={v} className="font-mono-genes">{v === "+" ? t.blood.rhPos : v === "-" ? t.blood.rhNeg : v}</span>]);
  return (
    <div className="border border-slate-200 rounded-md p-5 space-y-4" data-testid={`${id}-card`}>
      <div className="font-semibold">{label}</div>
      <Choice testId={`${id}-entry-mode`} value={state.mode} onChange={switchMode}
        options={[["type", t.blood.byType], ["genotype", t.blood.byGenotype]]} />
      <div><FieldLabel>{t.blood.abo}</FieldLabel><Choice testId={`${id}-abo`} value={state.abo} onChange={set("abo")} options={mono(ABO[state.mode])} /></div>
      <div><FieldLabel>{t.blood.rh}</FieldLabel><Choice testId={`${id}-rh`} value={state.rh} onChange={set("rh")} options={mono(RH[state.mode])} /></div>
    </div>
  );
};

export default function BloodTypePage() {
  const { t } = useLang();
  const { run, analysis, loading, error } = useAnalysis("blood-type");
  const [m, setM] = useState({ mode: "type", abo: "A", rh: "+" });
  const [f, setF] = useState({ mode: "type", abo: "O", rh: "+" });
  return (
    <CalcLayout kind="blood-type" loading={loading} error={error} analysis={analysis}
      onSubmit={() => run({ parent1_abo: m.abo, parent1_rh: m.rh, parent2_abo: f.abo, parent2_rh: f.rh })}>
      <div className="grid md:grid-cols-2 gap-6">
        <ParentInput id="mother" label={t.c.mother} state={m} setState={setM} />
        <ParentInput id="father" label={t.c.father} state={f} setState={setF} />
      </div>
    </CalcLayout>
  );
}

ParentInput.propTypes = {
  id: PropTypes.oneOf(["mother", "father"]).isRequired,
  label: PropTypes.string.isRequired,
  state: PropTypes.shape({ mode: PropTypes.oneOf(["type", "genotype"]), abo: PropTypes.string, rh: PropTypes.string }).isRequired,
  setState: PropTypes.func.isRequired,
};
