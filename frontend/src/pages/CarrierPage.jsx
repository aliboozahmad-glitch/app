import { useState } from "react";
import PropTypes from "prop-types";
import { useLang } from "@/i18n/LanguageContext";
import { useAnalysis, usePublic } from "@/lib/api";
import { CalcLayout } from "@/components/genova/CalcLayout";
import { LoadState } from "@/components/genova/LoadState";
import { Choice, FieldLabel } from "@/components/genova/primitives";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const MOTHER = ["affected", "carrier", "non_carrier", "unknown"];
const FATHER_AR = ["affected", "carrier", "non_carrier", "unknown"];
const FATHER_X = ["affected", "unaffected", "unknown"];

const isXLinked = (catalog, id) => catalog?.diseases.find((d) => d.id === id)?.inheritance === "x_linked_recessive";
const fatherOptionsFor = (x) => (x ? FATHER_X : FATHER_AR);

const DiseasePicker = ({ diseases, value, onChange }) => {
  const { t } = useLang();
  const disease = diseases.find((d) => d.id === value);
  return (
    <div className="max-w-md">
      <FieldLabel>{t.carrier.disease}</FieldLabel>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger data-testid="disease-select"><SelectValue /></SelectTrigger>
        <SelectContent>
          {diseases.map((d) => (
            <SelectItem key={d.id} value={d.id} data-testid={`disease-option-${d.id}`}>{d.name} · {d.gene}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      {disease && <p className="text-sm text-slate-500 mt-2" data-testid="disease-inheritance">{disease.inheritance_label}</p>}
    </div>
  );
};

DiseasePicker.propTypes = {
  diseases: PropTypes.arrayOf(PropTypes.shape({ id: PropTypes.string.isRequired, name: PropTypes.string.isRequired })).isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

const useCarrierForm = (catalog) => {
  const [form, setForm] = useState({ diseaseId: "beta_thalassemia", mother: "carrier", father: "carrier", region: "gulf" });
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));
  const pickDisease = (id) => setForm((f) => {
    const opts = fatherOptionsFor(isXLinked(catalog, id));
    return { ...f, diseaseId: id, father: opts.includes(f.father) ? f.father : opts[1] };
  });
  const unknown = form.mother === "unknown" || form.father === "unknown";
  const body = { disease_id: form.diseaseId, mother_status: form.mother, father_status: form.father, region: unknown ? form.region : null };
  return { form, set, pickDisease, unknown, body, fatherOpts: fatherOptionsFor(isXLinked(catalog, form.diseaseId)) };
};

export default function CarrierPage() {
  const { t } = useLang();
  const catalogState = usePublic("/catalog");
  const { run, analysis, loading, error } = useAnalysis("carrier-risk");
  const { form, set, pickDisease, unknown, body, fatherOpts } = useCarrierForm(catalogState.data);
  const st = (l) => l.map((s) => [s, t.carrier.status[s]]);

  return (
    <CalcLayout kind="carrier-risk" loading={loading} error={error} analysis={analysis} onSubmit={() => run(body)}>
      <LoadState state={catalogState} testId="catalog">
        {(catalog) => (
          <>
            <DiseasePicker diseases={catalog.diseases} value={form.diseaseId} onChange={pickDisease} />
            <div className="grid md:grid-cols-2 gap-6">
              <div><FieldLabel>{t.carrier.mother}</FieldLabel><Choice testId="mother-status" value={form.mother} onChange={set("mother")} options={st(MOTHER)} /></div>
              <div><FieldLabel>{t.carrier.father}</FieldLabel><Choice testId="father-status" value={form.father} onChange={set("father")} options={st(fatherOpts)} /></div>
            </div>
            {unknown && (
              <div>
                <FieldLabel>{t.carrier.region}</FieldLabel>
                <Choice testId="region-choice" value={form.region} onChange={set("region")} options={catalog.regions.map((r) => [r.id, r.label])} />
              </div>
            )}
          </>
        )}
      </LoadState>
    </CalcLayout>
  );
}
