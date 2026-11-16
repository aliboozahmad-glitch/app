import { errorMessage, pct, summarize } from "./format";
import { translations } from "@/i18n/translations";

describe("errorMessage", () => {
  it("uses the localized engine message", () => {
    expect(errorMessage({ response: { data: { detail: { code: "invalid_genotype", message: "Ungültiger Genotyp" } } } }, "x")).toBe("Ungültiger Genotyp");
  });
  it("joins validation errors", () => {
    const err = { response: { data: { detail: { code: "validation_error", errors: [{ field: "mother_cm", message: "too small" }] } } } };
    expect(errorMessage(err, "x")).toBe("mother_cm: too small");
  });
  it("passes plain string details through", () => {
    expect(errorMessage({ response: { data: { detail: "Not found" } } }, "x")).toBe("Not found");
  });
  it("falls back for network errors", () => {
    expect(errorMessage(new Error("Network"), "fallback")).toBe("fallback");
  });
});

describe("pct", () => {
  it("formats whole and fractional percentages", () => {
    expect(pct(0.25)).toBe("25%");
    expect(pct(1)).toBe("100%");
    expect(pct(0.0125)).toBe("1.25%");
  });
});

describe("summarize (translated)", () => {
  const { en, ar, de } = translations;
  const mendel = { analysis_type: "mendelian", request: { mode: "autosomal_recessive", parent1: "Aa", parent2: "Aa" } };
  const carrier = { analysis_type: "carrier-risk", request: { mother_status: "carrier", father_status: "unknown", region: "gulf" } };
  const pig = { analysis_type: "pigmentation", request: { trait: "eye_color", mother: "brown", father: "blue" } };

  it("English labels", () => {
    expect(summarize(mendel, en)).toBe("Autosomal recessive · Aa × Aa");
    expect(summarize(carrier, en)).toBe("Mother: Carrier (tested) × Father: Not tested / unknown · Gulf (GCC)");
    expect(summarize(pig, en)).toBe("Eye colour · Brown × Blue");
  });
  it("Arabic labels", () => {
    expect(summarize(mendel, ar)).toBe("جسمي متنحٍ · Aa × Aa");
    expect(summarize(carrier, ar)).toContain("دول الخليج");
    expect(summarize(pig, ar)).toBe("لون العين · بني × أزرق");
  });
  it("German labels", () => {
    expect(summarize(mendel, de)).toBe("Autosomal-rezessiv · Aa × Aa");
    expect(summarize(pig, de)).toBe("Augenfarbe · Braun × Blau");
  });
  it("never shows raw internal codes for any mode, status, region or colour", () => {
    [en, ar, de].forEach((t) => {
      Object.keys(t.modes).forEach((m) => expect(summarize({ analysis_type: "mendelian", request: { mode: m, parent1: "AA", parent2: "AA" } }, t)).not.toContain(m));
      Object.keys(t.regions).forEach((r) => expect(summarize({ ...carrier, request: { ...carrier.request, region: r } }, t)).not.toContain(r));
    });
  });
  it("other calculators", () => {
    expect(summarize({ analysis_type: "blood-type", request: { parent1_abo: "A", parent1_rh: "+", parent2_abo: "O", parent2_rh: "-" } }, en)).toBe("A+ × O-");
    expect(summarize({ analysis_type: "height", request: { mother_cm: 165, father_cm: 180 } }, en)).toBe("165 cm × 180 cm");
    expect(summarize({ analysis_type: "sex-ratio", request: {} }, en)).toBe("105 : 100");
    expect(summarize({ analysis_type: "unknown" }, en)).toBe("");
  });
});
