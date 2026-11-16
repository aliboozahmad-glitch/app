import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";
import { Show, SignIn, SignUp } from "@clerk/react";
import { ArrowRight, Fingerprint, ShieldCheck, BookOpen } from "lucide-react";
import { useLang } from "@/i18n/LanguageContext";
import { TierLegend } from "./Dashboard";

const AUTH_IMG = "https://images.unsplash.com/photo-1641903202531-bfa6bf0c6419?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600";

export function Landing() {
  const { t } = useLang();
  const feats = [["deterministic", Fingerprint, t.landing.f1t, t.landing.f1d], ["certainty", ShieldCheck, t.landing.f2t, t.landing.f2d], ["sources", BookOpen, t.landing.f3t, t.landing.f3d]];
  return (
    <>
      <Show when="signed-in"><Navigate to="/dashboard" replace /></Show>
      <section className="grid-paper border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-16 sm:py-24 grid lg:grid-cols-[1.2fr_1fr] gap-12 items-center">
          <div className="rise">
            <div className="text-xs uppercase tracking-[0.2em] font-semibold text-slate-500">{t.landing.overline}</div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mt-4 leading-[1.05]" data-testid="landing-title">{t.landing.title}</h1>
            <p className="text-base sm:text-lg text-slate-600 mt-6 max-w-xl">{t.landing.subtitle}</p>
            <div className="flex flex-wrap gap-3 mt-8">
              <Link to="/sign-up" data-testid="landing-cta-button" className="inline-flex items-center gap-2 bg-slate-900 text-white px-6 py-3 rounded-md font-medium hover:bg-slate-800 transition-colors">
                {t.landing.cta} <ArrowRight size={16} className="rtl:rotate-180" />
              </Link>
              <Link to="/sources" data-testid="landing-sources-button" className="inline-flex items-center px-6 py-3 rounded-md font-medium border border-slate-300 bg-white hover:border-slate-500 transition-colors">{t.landing.secondary}</Link>
            </div>
          </div>
          <div className="relative aspect-[4/5] max-h-[520px] rounded-md overflow-hidden bg-slate-900 rise" style={{ animationDelay: "120ms" }}>
            <img src={AUTH_IMG} alt="DNA double helix" className="w-full h-full object-cover opacity-80" />
            <div className="absolute bottom-0 inset-x-0 p-5 bg-slate-950/80 text-white font-mono-genes text-sm" dir="ltr">
              Aa × Aa → AA 1/4 · Aa 1/2 · aa 1/4
            </div>
          </div>
        </div>
      </section>
      <section className="max-w-7xl mx-auto px-4 sm:px-8 py-16 space-y-12">
        <div className="grid md:grid-cols-3 gap-6">
          {feats.map(([id, Icon, title, desc], i) => (
            <div key={id} className="bg-white border border-slate-200 rounded-md p-6" data-testid={`landing-feature-${i}`}>
              <Icon size={22} /><h2 className="text-lg font-semibold mt-4">{title}</h2><p className="text-sm text-slate-600 mt-2">{desc}</p>
            </div>
          ))}
        </div>
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">{t.landing.tiers}</h2>
          <TierLegend />
        </div>
      </section>
    </>
  );
}

const AuthLayout = ({ children }) => (
  <div className="grid lg:grid-cols-2 min-h-[calc(100vh-4rem)]">
    <div className="hidden lg:block relative bg-slate-900">
      <img src={AUTH_IMG} alt="" className="absolute inset-0 w-full h-full object-cover opacity-70" />
    </div>
    <div className="flex items-center justify-center p-6">{children}</div>
  </div>
);

export const SignInPage = () => (
  <AuthLayout><SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" withSignUp /></AuthLayout>
);
export const SignUpPage = () => (
  <AuthLayout><SignUp routing="path" path="/sign-up" signInUrl="/sign-in" /></AuthLayout>
);

AuthLayout.propTypes = { children: PropTypes.node.isRequired };
