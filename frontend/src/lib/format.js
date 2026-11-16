/** Pure formatting helpers (no React, no network) so they can be unit-tested. */

const formatErrors = (errors) => errors.map((e) => `${e.field}: ${e.message}`).join(" · ");

const detailText = (d) => {
  if (typeof d === "string") return d;
  if (d.message) return d.message;
  return d.errors ? formatErrors(d.errors) : null;
};

/** @param {any} err axios error @param {string} fallback @returns {string} user-facing message */
export const errorMessage = (err, fallback) => {
  const d = err && err.response && err.response.data ? err.response.data.detail : null;
  return (d && detailText(d)) || fallback;
};

/** @param {number} p probability 0..1 @returns {string} e.g. "25%" or "1.25%" */
export const pct = (p) => `${(p * 100).toFixed((p * 100) % 1 === 0 ? 0 : 2)}%`;

const SUMMARIES = {
  mendelian: (r) => `${r.mode} · ${r.parent1} × ${r.parent2}`,
  "blood-type": (r) => `${r.parent1_abo}${r.parent1_rh} × ${r.parent2_abo}${r.parent2_rh}`,
  "carrier-risk": (r) => `${r.mother_status} × ${r.father_status}${r.region ? ` · ${r.region}` : ""}`,
  height: (r) => `${r.mother_cm} cm × ${r.father_cm} cm`,
  pigmentation: (r) => `${r.trait} · ${r.mother} × ${r.father}`,
  "sex-ratio": () => "105 : 100",
};

/** @param {{ analysis_type: string, request?: Object }} item history item @returns {string} one-line input summary */
export const summarize = ({ analysis_type: kind, request = {} }) => (SUMMARIES[kind] ? SUMMARIES[kind](request) : "");
