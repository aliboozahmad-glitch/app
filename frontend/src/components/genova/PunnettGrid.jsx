import { useLang } from "@/i18n/LanguageContext";

const recessiveOnly = (g) => g.replace(/X|Y/g, "") === g.replace(/X|Y/g, "").toLowerCase() && /[a-z]/.test(g);

export const PunnettGrid = ({ grid }) => {
  const { t } = useLang();
  return (
    <div data-testid="punnett-grid">
      <h3 className="text-xs uppercase tracking-[0.18em] font-semibold text-slate-500 mb-3">{t.c.grid}</h3>
      <div dir="ltr" className="inline-grid border border-slate-300 font-mono-genes"
        style={{ gridTemplateColumns: `repeat(${grid.columns.length + 1}, minmax(64px, 88px))` }}>
        <div className="bg-slate-50 border-e border-b border-slate-300" />
        {grid.columns.map((c, i) => (
          <div key={`c${i}`} className="bg-slate-900 text-white text-center py-2 text-sm border-b border-slate-300">{c}</div>
        ))}
        {grid.rows.map((r, ri) => [
          <div key={`r${ri}`} className="bg-slate-900 text-white text-center py-3 text-sm border-e border-slate-300 grid place-items-center">{r}</div>,
          ...grid.cells[ri].map((cell, ci) => (
            <div key={`${ri}-${ci}`} data-testid={`punnett-cell-${ri}-${ci}`}
              className={`text-center py-3 text-base font-semibold border-slate-200 ${ci < grid.columns.length - 1 ? "border-e" : ""} ${ri < grid.rows.length - 1 ? "border-b" : ""} ${recessiveOnly(cell) ? "bg-amber-50" : "bg-white"}`}>
              {cell}
            </div>
          )),
        ])}
      </div>
    </div>
  );
};
