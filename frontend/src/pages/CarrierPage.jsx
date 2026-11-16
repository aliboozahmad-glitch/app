import { useState } from "react";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis, usePublic } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { Choice, FieldLabel } from "@/components/genova/primitives";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const MOTHER = ["affected", "carrier", "non_carrier", "unknown"];
const FATHER_AR = ["affected", "carrier", "non_carrier", "unknown"];
const FATHER_X = ["affected", "unaffected", "unknown"];

export default function CarrierPage() {
  const { t } = useLang();
  const catalog = usePublic("/catalog");
  const { run, analysis, loading, error } = useAnalysis("carrier-risk");
  const [diseaseId, setDiseaseId] = useState("beta_thalassemia");
  const [mother, setMother] = useState("carrier");
  const [father, setFather] = useState("carrier");
  const [region, setRegion] = useState("gulf");

  const disease = catalog?.diseases.find((d) => d.id === diseaseId);
  const xLinked = disease?.inheritance === "x_linked_recessive";
  const fatherOpts = xLinked ? FATHER_X : FATHER_AR;
  const unknown = mother === "unknown" || father === "unknown";
  const st = (l) => l.map((s) => [s, t.carrier.status[s]]);

  const pickDisease = (id) => {
    setDiseaseId(id);
    const x = catalog.diseases.find((d) => d.id === id).inheritance === "x_linked_recessive";
    if (!(x ? FATHER_X : FATHER_AR).includes(father)) setFather(x ? "unaffected" : "carrier");
  };

  return (
    <CalcLayout kind="carrier-risk" loading={loading} error={error} analysis={analysis}
      onSubmit={() => run({ disease_id: diseaseId, mother_status: mother, father_status: father, region: unknown ? region : null })}>
      <div className="max-w-md">
        <FieldLabel>{t.carrier.disease}</FieldLabel>
        <Select value={diseaseId} onValueChange={pickDisease}>
          <SelectTrigger data-testid="disease-select"><SelectValue /></SelectTrigger>
          <SelectContent>
            {catalog?.diseases.map((d) => (
              <SelectItem key={d.id} value={d.id} data-testid={`disease-option-${d.id}`}>{d.name} · {d.gene}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {disease && <p className="text-sm text-slate-500 mt-2" data-testid="disease-inheritance">{disease.inheritance_label}</p>}
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <div><FieldLabel>{t.carrier.mother}</FieldLabel><Choice testId="mother-status" value={mother} onChange={setMother} options={st(MOTHER)} /></div>
        <div><FieldLabel>{t.carrier.father}</FieldLabel><Choice testId="father-status" value={father} onChange={setFather} options={st(fatherOpts)} /></div>
      </div>
      {unknown && catalog && (
        <div>
          <FieldLabel>{t.carrier.region}</FieldLabel>
          <Choice testId="region-choice" value={region} onChange={setRegion} options={catalog.regions.map((r) => [r.id, r.label])} />
        </div>
      )}
    </CalcLayout>
  );
}
