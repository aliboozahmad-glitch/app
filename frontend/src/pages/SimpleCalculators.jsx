import { useState } from "react";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { Choice, FieldLabel } from "@/components/genova/primitives";
import { Input } from "@/components/ui/input";

export function HeightPage() {
  const { t } = useLang();
  const { run, analysis, loading, error } = useAnalysis("height");
  const [m, setM] = useState("165");
  const [f, setF] = useState("178");
  return (
    <CalcLayout kind="height" loading={loading} error={error} analysis={analysis}
      onSubmit={() => run({ mother_cm: Number(m), father_cm: Number(f) })}>
      <div className="grid sm:grid-cols-2 gap-6 max-w-xl">
        <div><FieldLabel>{t.height.mother}</FieldLabel><Input type="number" min="120" max="230" step="0.5" required value={m} onChange={(e) => setM(e.target.value)} data-testid="mother-height-input" /></div>
        <div><FieldLabel>{t.height.father}</FieldLabel><Input type="number" min="120" max="230" step="0.5" required value={f} onChange={(e) => setF(e.target.value)} data-testid="father-height-input" /></div>
      </div>
    </CalcLayout>
  );
}

const COLOURS = { eye_color: ["brown", "hazel", "green", "blue", "gray"], hair_color: ["black", "brown", "blonde", "red"] };

export function PigmentationPage() {
  const { t } = useLang();
  const { run, analysis, loading, error } = useAnalysis("pigmentation");
  const [trait, setTrait] = useState("eye_color");
  const [m, setM] = useState("brown");
  const [f, setF] = useState("blue");
  const opts = COLOURS[trait].map((c) => [c, t.traits.colours[c]]);
  const pickTrait = (tr) => { setTrait(tr); setM(COLOURS[tr][0]); setF(COLOURS[tr][1]); };
  return (
    <CalcLayout kind="pigmentation" loading={loading} error={error} analysis={analysis} onSubmit={() => run({ trait, mother: m, father: f })}>
      <div><FieldLabel>{t.traits.trait}</FieldLabel>
        <Choice testId="trait-choice" value={trait} onChange={pickTrait} options={[["eye_color", t.traits.eye_color], ["hair_color", t.traits.hair_color]]} /></div>
      <div className="grid md:grid-cols-2 gap-6">
        <div><FieldLabel>{t.c.mother}</FieldLabel><Choice testId="mother-colour" value={m} onChange={setM} options={opts} /></div>
        <div><FieldLabel>{t.c.father}</FieldLabel><Choice testId="father-colour" value={f} onChange={setF} options={opts} /></div>
      </div>
    </CalcLayout>
  );
}

export function SexRatioPage() {
  const { t } = useLang();
  const { run, analysis, loading, error } = useAnalysis("sex-ratio");
  return (
    <CalcLayout kind="sex-ratio" loading={loading} error={error} analysis={analysis} onSubmit={() => run({})}>
      <p className="text-slate-700 max-w-2xl" data-testid="sex-ratio-intro">{t.sex.intro}</p>
    </CalcLayout>
  );
}
