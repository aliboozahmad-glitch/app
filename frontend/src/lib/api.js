import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@clerk/react";
import { useLang } from "@/i18n/LanguageContext";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const useApi = () => {
  const { getToken } = useAuth();
  return useCallback(async (method, path, data) => {
    const token = await getToken();
    const res = await axios({ method, url: `${API}${path}`, data, headers: { Authorization: `Bearer ${token}` } });
    return res.data;
  }, [getToken]);
};

export const errorMessage = (err, fallback) => {
  const d = err?.response?.data?.detail;
  if (d?.message) return d.message;
  if (d?.errors) return d.errors.map((e) => `${e.field}: ${e.message}`).join(" · ");
  if (typeof d === "string") return d;
  return fallback;
};

// Runs an analysis, then re-fetches the saved result whenever the language changes.
export const useAnalysis = (kind) => {
  const api = useApi();
  const { lang, t } = useLang();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async (body) => {
    setLoading(true);
    setError(null);
    try {
      setAnalysis(await api("post", `/analyses/${kind}?lang=${lang}`, body));
    } catch (e) {
      setError(errorMessage(e, t.c.error));
    } finally {
      setLoading(false);
    }
  };

  const id = analysis?.id;
  useEffect(() => {
    if (!id) return;
    api("get", `/analyses/${id}?lang=${lang}`).then(setAnalysis).catch(() => {});
  }, [lang, id, api]);

  return { run, analysis, loading, error };
};

export const usePublic = (path) => {
  const { lang } = useLang();
  const [data, setData] = useState(null);
  useEffect(() => {
    axios.get(`${API}${path}${path.includes("?") ? "&" : "?"}lang=${lang}`).then((r) => setData(r.data));
  }, [path, lang]);
  return data;
};
