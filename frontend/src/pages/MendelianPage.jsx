import { useState } from "react";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { Choice, FieldLabel } from "@/components/genova/primitives";

const GENOTYPES = {
  autosomal_dominant: [["AA", "Aa", "aa"], ["AA", "Aa", "aa"]],
  autosomal_recessive: [["AA", "Aa", "aa"], ["AA", "Aa", "aa"]],
  codominant: [["AA", "AB", "BB"], ["AA", "AB", "BB"]],
  incomplete_dominance: [["AA", "AB", "BB"], ["AA", "AB", "BB"]],
  x_linked_recessive: [["XAXA", "XAXa", "XaXa"], ["XAY", "XaY"]],
  x_linked_dominant: [["XAXA", "XAXa", "XaXa"], ["XAY", "XaY"]],
};
const MODE_LABEL = {
  en: { autosomal_dominant: "Autosomal dominant", autosomal_recessive: "Autosomal recessive", codominant: "Codominant", incomplete_dominance: "Incomplete dominance", x_linked_recessive: "X-linked recessive", x_linked_dominant: "X-linked dominant" },
  ar: { autosomal_dominant: "جسمي سائد", autosomal_recessive: "جسمي متنحٍ", codominant: "سيادة مشتركة", incomplete_dominance: "سيادة غير تامة", x_linked_recessive: "متنحٍ مرتبط بـ X", x_linked_dominant: "سائد مرتبط بـ X" },
  de: { autosomal_dominant: "Autosomal-dominant", autosomal_recessive: "Autosomal-rezessiv", codominant: "Kodominant", incomplete_dominance: "Unvollständige Dominanz", x_linked_recessive: "X-rezessiv", x_linked_dominant: "X-dominant" },
};

export default function MendelianPage() {
  const { t, lang } = useLang();
  const { run, analysis, loading, error } = useAnalysis("mendelian");
  const [mode, setMode] = useState("autosomal_recessive");
  const [p1, setP1] = useState("Aa");
  const [p2, setP2] = useState("Aa");
  const isX = mode.startsWith("x_");
  const [g1, g2] = GENOTYPES[mode];

  const changeMode = (m) => { setMode(m); setP1(GENOTYPES[m][0][1]); setP2(GENOTYPES[m][1][0]); };
  const opts = (list) => list.map((g) => [g, <span className="font-mono-genes">{g}</span>]);
  const hint = isX ? t.mendelian.hintX : mode.includes("dominance") || mode === "codominant" ? t.mendelian.hintCo : t.mendelian.hintAuto;

  return (
    <CalcLayout kind="mendelian" onSubmit={() => run({ mode, parent1: p1, parent2: p2 })} loading={loading} error={error} analysis={analysis}>
      <div>
        <FieldLabel>{t.mendelian.mode}</FieldLabel>
        <Choice testId="mode-choice" value={mode} onChange={changeMode} options={Object.keys(GENOTYPES).map((m) => [m, MODE_LABEL[lang][m]])} />
        <p className="text-sm text-slate-500 mt-2" data-testid="mode-hint">{hint}</p>
      </div>
      <div className="grid sm:grid-cols-2 gap-6">
        <div><FieldLabel>{isX ? t.c.mother : t.c.parent1}</FieldLabel><Choice testId="parent1-choice" value={p1} onChange={setP1} options={opts(g1)} /></div>
        <div><FieldLabel>{isX ? t.c.father : t.c.parent2}</FieldLabel><Choice testId="parent2-choice" value={p2} onChange={setP2} options={opts(g2)} /></div>
      </div>
    </CalcLayout>
  );
}
