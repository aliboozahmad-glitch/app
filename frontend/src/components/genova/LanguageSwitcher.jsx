import { useLang } from "@/i18n/LanguageContext";

const LANGS = [["en", "EN"], ["ar", "عربي"], ["de", "DE"]];

export const LanguageSwitcher = () => {
  const { lang, setLang } = useLang();
  return (
    <div className="flex border border-slate-200 rounded-md overflow-hidden" data-testid="language-switcher">
      {LANGS.map(([code, label]) => (
        <button
          key={code}
          onClick={() => setLang(code)}
          data-testid={`lang-${code}-button`}
          className={`text-xs px-2.5 py-1.5 font-semibold transition-colors ${lang === code ? "bg-slate-900 text-white" : "bg-white text-slate-600 hover:bg-slate-100"}`}
        >
          {label}
        </button>
      ))}
    </div>
  );
};
