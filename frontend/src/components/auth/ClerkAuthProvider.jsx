import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ClerkProvider } from "@clerk/react";

const appearance = {
  variables: {
    colorPrimary: "#0F172A",
    colorPrimaryForeground: "#FFFFFF",
    colorBackground: "#FFFFFF",
    colorForeground: "#020617",
    colorBorder: "#E2E8F0",
    fontFamily: "'IBM Plex Sans', 'IBM Plex Sans Arabic', sans-serif",
    borderRadius: "0.375rem",
  },
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ClerkAuthProvider({ children }) {
  const navigate = useNavigate();
  const [config, setConfig] = useState(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async (attempt = 0) => {
      try {
        const cfg = await (await fetch(`${BACKEND_URL}/api/clerk/config`)).json();
        if (cfg.enabled) return cancelled || setConfig(cfg);
      } catch {
        // Backend not reachable yet: handled by the retry below, then the "unavailable" message.
      }
      if (cancelled) return;
      if (attempt >= 20) return setUnavailable(true);
      setTimeout(() => load(attempt + 1), 1500);
    };
    load();
    return () => { cancelled = true; };
  }, []);

  if (unavailable) return <p style={{ padding: 24 }}>Sign-in is unavailable right now. Refresh the page to try again.</p>;
  if (!config) return null;
  return (
    <ClerkProvider
      publishableKey={config.publishable_key}
      proxyUrl={config.proxy_url || undefined}
      appearance={appearance}
      routerPush={(to) => navigate(to)}
      routerReplace={(to) => navigate(to, { replace: true })}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/dashboard"
      signUpFallbackRedirectUrl="/dashboard"
      afterSignOutUrl="/"
    >
      {children}
    </ClerkProvider>
  );
}

ClerkAuthProvider.propTypes = { children: PropTypes.node.isRequired };
