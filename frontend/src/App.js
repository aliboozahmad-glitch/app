import PropTypes from "prop-types";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Show } from "@clerk/react";
import ClerkAuthProvider from "@/components/auth/ClerkAuthProvider";
import { LanguageProvider } from "@/i18n/LanguageContext";
import { AppShell } from "@/components/genova/AppShell";
import { Toaster } from "@/components/ui/sonner";
import { Landing, SignInPage, SignUpPage } from "@/pages/PublicPages";
import Dashboard from "@/pages/Dashboard";
import MendelianPage from "@/pages/MendelianPage";
import BloodTypePage from "@/pages/BloodTypePage";
import CarrierPage from "@/pages/CarrierPage";
import { HeightPage, PigmentationPage, SexRatioPage } from "@/pages/SimpleCalculators";
import { AnalysisDetailPage, HistoryPage } from "@/pages/HistoryPages";
import SourcesPage from "@/pages/SourcesPage";
import FamilyPatternPage from "@/pages/FamilyPatternPage";

const Protected = ({ children }) => (
  <>
    <Show when="signed-in">{children}</Show>
    <Show when="signed-out"><Navigate to="/sign-in" replace /></Show>
  </>
);

Protected.propTypes = { children: PropTypes.node.isRequired };

const p = (el) => <Protected>{el}</Protected>;

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <ClerkAuthProvider>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<Landing />} />
              <Route path="/sign-in/*" element={<SignInPage />} />
              <Route path="/sign-up/*" element={<SignUpPage />} />
              <Route path="/sources" element={<SourcesPage />} />
              <Route path="/dashboard" element={p(<Dashboard />)} />
              <Route path="/calc/mendelian" element={p(<MendelianPage />)} />
              <Route path="/calc/blood-type" element={p(<BloodTypePage />)} />
              <Route path="/calc/carrier-risk" element={p(<CarrierPage />)} />
              <Route path="/calc/height" element={p(<HeightPage />)} />
              <Route path="/calc/pigmentation" element={p(<PigmentationPage />)} />
              <Route path="/calc/sex-ratio" element={p(<SexRatioPage />)} />
              <Route path="/calc/family-pattern" element={p(<FamilyPatternPage />)} />
              <Route path="/history" element={p(<HistoryPage />)} />
              <Route path="/history/:id" element={p(<AnalysisDetailPage />)} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
          <Toaster position="top-center" />
        </ClerkAuthProvider>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
