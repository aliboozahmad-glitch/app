import { errorMessage, pct, summarize } from "./format";

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

describe("summarize", () => {
  it("summarizes each calculator's inputs", () => {
    expect(summarize({ analysis_type: "mendelian", request: { mode: "autosomal_recessive", parent1: "Aa", parent2: "Aa" } })).toBe("autosomal_recessive · Aa × Aa");
    expect(summarize({ analysis_type: "blood-type", request: { parent1_abo: "A", parent1_rh: "+", parent2_abo: "O", parent2_rh: "-" } })).toBe("A+ × O-");
    expect(summarize({ analysis_type: "carrier-risk", request: { mother_status: "carrier", father_status: "unknown", region: "gulf" } })).toBe("carrier × unknown · gulf");
    expect(summarize({ analysis_type: "height", request: { mother_cm: 165, father_cm: 180 } })).toBe("165 cm × 180 cm");
    expect(summarize({ analysis_type: "sex-ratio", request: {} })).toBe("");
  });
});
