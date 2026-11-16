/** Pure formatting helpers (no React, no network) so they can be unit-tested. */

/** @returns {string} translated, ordered list of children, e.g. "Boy, Girl" */
export const familyNames = (list, t) => list.map((g) => (g === "male" ? t.family.boy : t.family.girl)).join(t.family.sep);

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

const label = (map, key) => (map && map[key]) || key;

const SUMMARIES = {
  mendelian: (r, t) => `${label(t.modes, r.mode)} · ${r.parent1} × ${r.parent2}`,
  "blood-type": (r) => `${r.parent1_abo}${r.parent1_rh} × ${r.parent2_abo}${r.parent2_rh}`,
  "carrier-risk": (r, t) => {
    const status = (s) => label(t.carrier.status, s);
    const region = r.region ? ` · ${label(t.regions, r.region)}` : "";
    return `${t.c.mother}: ${status(r.mother_status)} × ${t.c.father}: ${status(r.father_status)}${region}`;
  },
  height: (r) => `${r.mother_cm} cm × ${r.father_cm} cm`,
  pigmentation: (r, t) => `${label(t.traits, r.trait)} · ${label(t.traits.colours, r.mother)} × ${label(t.traits.colours, r.father)}`,
  "sex-ratio": () => "105 : 100",
  "family-pattern": (r, t) => {
    const child = { 1: ` · ${t.family.first}`, 2: ` · ${t.family.second}` }[r.child_number] || "";
    return `${t.family.wifeShort}: ${familyNames(r.wife, t)} × ${t.family.husbandShort}: ${familyNames(r.husband, t)}${child}`;
  },
};

/**
 * @param {{ analysis_type: string, request?: Object }} item history item
 * @param {Object} t translations for the current language
 * @returns {string} one-line, translated input summary
 */
export const summarize = ({ analysis_type: kind, request = {} }, t) => (SUMMARIES[kind] ? SUMMARIES[kind](request, t) : "");
