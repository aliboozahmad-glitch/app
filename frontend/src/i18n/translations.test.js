import { readFileSync } from "fs";
import { join } from "path";
import { translations } from "./translations";

const keysOf = (obj, prefix = "") =>
  Object.entries(obj).flatMap(([k, v]) => (v && typeof v === "object" && !Array.isArray(v) ? keysOf(v, `${prefix}${k}.`) : [`${prefix}${k}`]));

describe("translations", () => {
  it("Arabic and German define every English key", () => {
    const en = keysOf(translations.en).sort();
    expect(keysOf(translations.ar).sort()).toEqual(en);
    expect(keysOf(translations.de).sort()).toEqual(en);
  });

  it("no production console statements in app source", () => {
    const files = ["lib/api.js", "lib/format.js", "App.js", "i18n/LanguageContext.jsx"];
    files.forEach((f) => expect(readFileSync(join(__dirname, "..", f), "utf8")).not.toMatch(/console\./));
  });
});
