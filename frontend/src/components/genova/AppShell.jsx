import { Link, NavLink, Outlet } from "react-router-dom";
import { Show, SignInButton, UserButton } from "@clerk/react";
import { Dna } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { LanguageSwitcher } from "./LanguageSwitcher";

const navCls = ({ isActive }) =>
  `text-sm px-3 py-2 rounded-md transition-colors ${isActive ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"}`;

export const AppShell = () => {
  const { t } = useLang();
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-30 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 h-16 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 me-4" data-testid="brand-home-link">
            <span className="w-8 h-8 bg-slate-900 text-white grid place-items-center rounded-sm"><Dna size={18} /></span>
            <span className="font-display font-extrabold tracking-tight text-lg">GENOVA<span className="text-slate-400">AI</span></span>
          </Link>
          <nav className="hidden md:flex items-center gap-1">
            <Show when="signed-in">
              <NavLink to="/dashboard" className={navCls} data-testid="nav-dashboard">{t.nav.dashboard}</NavLink>
              <NavLink to="/history" className={navCls} data-testid="nav-history">{t.nav.history}</NavLink>
            </Show>
            <NavLink to="/sources" className={navCls} data-testid="nav-sources">{t.nav.sources}</NavLink>
          </nav>
          <div className="ms-auto flex items-center gap-3">
            <LanguageSwitcher />
            <Show when="signed-out">
              <SignInButton>
                <button className="text-sm font-medium bg-slate-900 text-white px-4 py-2 rounded-md hover:bg-slate-800 transition-colors" data-testid="header-sign-in-button">{t.nav.signIn}</button>
              </SignInButton>
            </Show>
            <Show when="signed-in"><div data-testid="user-menu"><UserButton /></div></Show>
          </div>
        </div>
        <Show when="signed-in">
          <nav className="md:hidden flex gap-1 px-4 pb-2 overflow-x-auto">
            <NavLink to="/dashboard" className={navCls} data-testid="mobile-nav-dashboard">{t.nav.dashboard}</NavLink>
            <NavLink to="/history" className={navCls} data-testid="mobile-nav-history">{t.nav.history}</NavLink>
            <NavLink to="/sources" className={navCls} data-testid="mobile-nav-sources">{t.nav.sources}</NavLink>
          </nav>
        </Show>
      </header>
      <main className="flex-1"><Outlet /></main>
      <footer className="border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-6 text-xs text-slate-500 flex flex-col sm:flex-row gap-2 justify-between">
          <span data-testid="footer-disclaimer">{t.disclaimer}</span>
          <span className="font-mono-genes">genova-genetics 1.0.0</span>
        </div>
      </footer>
    </div>
  );
};
