import { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { useAuth } from "@clerk/react";
import { useLang } from "@/i18n/LanguageContext";
import { errorMessage } from "./format";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/** @returns {(method: string, path: string, data?: Object) => Promise<any>} authenticated API caller */
export const useApi = () => {
  const { getToken } = useAuth();
  return useCallback(async (method, path, data) => {
    const token = await getToken();
    const res = await axios({ method, url: `${API}${path}`, data, headers: { Authorization: `Bearer ${token}` } });
    return res.data;
  }, [getToken]);
};

export { errorMessage } from "./format";

/**
 * Runs an analysis, then re-fetches the saved result whenever the language changes.
 * @param {string} kind calculator id, e.g. "mendelian"
 * @returns {{ run: (body: Object) => Promise<void>, analysis: (import("@/types").Analysis|null), loading: boolean, error: (string|null) }}
 */
export const useAnalysis = (kind) => {
  const api = useApi();
  const { lang, t } = useLang();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const inFlight = useRef(false);
  // One click = one calculation: further submits are ignored until the current one finishes.
  const run = async (body) => {
    if (inFlight.current) return;
    inFlight.current = true;
    setLoading(true);
    setError(null);
    try {
      setAnalysis(await api("post", `/analyses/${kind}?lang=${lang}`, body));
    } catch (e) {
      setError(errorMessage(e, t.c.error));
    } finally {
      inFlight.current = false;
      setLoading(false);
    }
  };

  const id = analysis?.id;
  const loadedLang = analysis?.result?.lang;
  const fallback = t.c.error;
  useEffect(() => {
    if (!id || loadedLang === lang) return undefined;
    let active = true;
    api("get", `/analyses/${id}?lang=${lang}`)
      .then((a) => { if (active) { setAnalysis(a); setError(null); } })
      .catch((e) => active && setError(errorMessage(e, fallback)));
    return () => { active = false; };
  }, [lang, id, loadedLang, api, fallback]);

  return { run, analysis, loading, error };
};

/**
 * Public (no-auth) GET with loading, error and retry. Ignores responses from stale language requests.
 * @param {string} path e.g. "/catalog"
 * @returns {{ data: any, loading: boolean, error: boolean, retry: () => void }}
 */
export const usePublic = (path) => {
  const { lang } = useLang();
  const [state, setState] = useState({ data: null, loading: true, error: false });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setState((s) => ({ ...s, loading: true, error: false }));
    const sep = path.includes("?") ? "&" : "?";
    axios.get(`${API}${path}${sep}lang=${lang}`)
      .then((r) => active && setState({ data: r.data, loading: false, error: false }))
      .catch(() => active && setState((s) => ({ ...s, loading: false, error: true })));
    return () => { active = false; };
  }, [path, lang, attempt]);
  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  return { ...state, retry };
};

/**
 * Signed-in GET with loading, error, retry and a forbidden flag for admin-only data.
 * @param {string} path e.g. "/admin/stats"
 */
export const useAuthedGet = (path) => {
  const api = useApi();
  const [state, setState] = useState({ data: null, error: false, forbidden: false });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setState((s) => ({ ...s, error: false }));
    api("get", path)
      .then((data) => active && setState({ data, error: false, forbidden: false }))
      .catch((e) => active && setState((s) => ({ ...s, error: true, forbidden: e?.response?.status === 403 })));
    return () => { active = false; };
  }, [api, path, attempt]);
  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  return { ...state, retry };
};

/** @returns {{ role: string }|null} the signed-in member, or null while loading / signed out */
export const useMe = () => {
  const { isSignedIn } = useAuth();
  const api = useApi();
  const [me, setMe] = useState(null);
  useEffect(() => {
    if (!isSignedIn) { setMe(null); return undefined; }
    let active = true;
    api("get", "/me").then((m) => active && setMe(m)).catch(() => active && setMe(null));
    return () => { active = false; };
  }, [api, isSignedIn]);
  return me;
};
