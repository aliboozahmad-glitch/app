import PropTypes from "prop-types";

/**
 * @typedef {"established"|"population_estimate"|"statistical_estimate"|"uncertain_estimate"|"population_statistic"} CertaintyTier
 * @typedef {{ key: string, kind: "phenotype"|"genotype"|"blood_type"|"measurement"|"qualitative", group: string,
 *   label: string, group_label: string, probability: (number|null), fraction: (string|null),
 *   range?: number[], range_fraction?: string[], value?: number, unit?: string }} Outcome
 * @typedef {{ key: string, text: string }} Note
 * @typedef {{ id: string, title: string, publisher: string, url: string, link_check: string }} Reference
 * @typedef {{ mother_genotype: string, father_genotype: string, outcomes: Outcome[] }} Scenario
 * @typedef {{ columns: string[], rows: string[], cells: string[][] }} Grid
 * @typedef {{ certainty: CertaintyTier, certainty_label: string, method: string, method_label: string,
 *   outcomes: Outcome[], assumptions: Note[], limitations: Note[], references: Reference[],
 *   details: Object, engine_version: string, data_version: (string|null) }} LocalizedResult
 * @typedef {{ id: string, analysis_type: string, created_at: string, request: Object, result: LocalizedResult }} Analysis
 */

export const TIERS = ["established", "population_estimate", "statistical_estimate", "uncertain_estimate", "population_statistic"];

export const outcomeShape = PropTypes.shape({
  key: PropTypes.string.isRequired,
  kind: PropTypes.string.isRequired,
  group: PropTypes.string.isRequired,
  label: PropTypes.string,
  group_label: PropTypes.string,
  probability: PropTypes.number,
  fraction: PropTypes.string,
  range: PropTypes.arrayOf(PropTypes.number),
  range_fraction: PropTypes.arrayOf(PropTypes.string),
  value: PropTypes.number,
  unit: PropTypes.string,
});

export const noteShape = PropTypes.shape({ key: PropTypes.string.isRequired, text: PropTypes.string.isRequired });

export const referenceShape = PropTypes.shape({
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  publisher: PropTypes.string,
  url: PropTypes.string.isRequired,
  link_check: PropTypes.string,
});

export const gridShape = PropTypes.shape({
  columns: PropTypes.arrayOf(PropTypes.string).isRequired,
  rows: PropTypes.arrayOf(PropTypes.string).isRequired,
  cells: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
});

export const scenarioShape = PropTypes.shape({
  mother_genotype: PropTypes.string.isRequired,
  father_genotype: PropTypes.string.isRequired,
  outcomes: PropTypes.arrayOf(outcomeShape).isRequired,
});

export const resultShape = PropTypes.shape({
  certainty: PropTypes.oneOf(TIERS).isRequired,
  certainty_label: PropTypes.string.isRequired,
  method: PropTypes.string.isRequired,
  method_label: PropTypes.string.isRequired,
  outcomes: PropTypes.arrayOf(outcomeShape).isRequired,
  assumptions: PropTypes.arrayOf(noteShape).isRequired,
  limitations: PropTypes.arrayOf(noteShape).isRequired,
  references: PropTypes.arrayOf(referenceShape).isRequired,
  details: PropTypes.object,
  engine_version: PropTypes.string,
  data_version: PropTypes.string,
});

export const analysisShape = PropTypes.shape({
  id: PropTypes.string.isRequired,
  analysis_type: PropTypes.string.isRequired,
  created_at: PropTypes.string,
  request: PropTypes.object,
  result: resultShape.isRequired,
});
