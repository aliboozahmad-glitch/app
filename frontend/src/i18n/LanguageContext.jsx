import { createContext, useContext, useEffect, useState } from "react";
import { translations } from "./translations";

const LangContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState(() => localStorage.getItem("genova-lang") || "en");
  useEffect(() => {
    localStorage.setItem("genova-lang", lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);
  return <LangContext.Provider value={{ lang, setLang, t: translations[lang] }}>{children}</LangContext.Provider>;
};

export const useLang = () => useContext(LangContext);
