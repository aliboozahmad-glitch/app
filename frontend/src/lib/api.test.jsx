import { act, renderHook, waitFor } from "@testing-library/react";
import axios from "axios";
import { LanguageProvider } from "@/i18n/LanguageContext";
import { useAnalysis, usePublic } from "./api";

jest.mock("axios", () => {
  const fn = jest.fn();
  fn.get = jest.fn();
  return { __esModule: true, default: fn };
});
jest.mock("@clerk/react", () => ({ useAuth: () => ({ getToken: () => Promise.resolve("test-token") }) }));

const wrapper = ({ children }) => <LanguageProvider>{children}</LanguageProvider>;

beforeEach(() => {
  localStorage.setItem("genova-lang", "en");
  axios.mockReset();
  axios.get.mockReset();
});

describe("usePublic", () => {
  it("starts loading, then returns data", async () => {
    axios.get.mockResolvedValueOnce({ data: { diseases: [1, 2] } });
    const { result } = renderHook(() => usePublic("/catalog"), { wrapper });
    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.data).toEqual({ diseases: [1, 2] }));
    expect(result.current.error).toBe(false);
    expect(axios.get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/catalog\?lang=en$/));
  });

  it("reports an error, and retry recovers", async () => {
    axios.get.mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce({ data: { ok: true } });
    const { result } = renderHook(() => usePublic("/catalog"), { wrapper });
    await waitFor(() => expect(result.current.error).toBe(true));
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    act(() => result.current.retry());
    await waitFor(() => expect(result.current.data).toEqual({ ok: true }));
    expect(result.current.error).toBe(false);
    expect(axios.get).toHaveBeenCalledTimes(2);
  });
});

describe("useAnalysis", () => {
  const saved = { id: "a1", analysis_type: "mendelian", result: { lang: "en" } };

  it("rapid repeated clicks create exactly one calculation request", async () => {
    let resolve;
    axios.mockReturnValueOnce(new Promise((r) => { resolve = r; }));
    const { result } = renderHook(() => useAnalysis("mendelian"), { wrapper });
    act(() => { result.current.run({ mode: "autosomal_recessive", parent1: "Aa", parent2: "Aa" }); });
    act(() => { result.current.run({ mode: "autosomal_recessive", parent1: "Aa", parent2: "Aa" }); });
    act(() => { result.current.run({ mode: "autosomal_recessive", parent1: "Aa", parent2: "Aa" }); });
    expect(result.current.loading).toBe(true);
    await act(async () => resolve({ data: saved }));
    await waitFor(() => expect(result.current.analysis).toEqual(saved));
    expect(axios).toHaveBeenCalledTimes(1);
    expect(axios.mock.calls[0][0]).toMatchObject({ method: "post", headers: { Authorization: "Bearer test-token" } });
    expect(result.current.loading).toBe(false);
  });

  it("a new click is accepted after the previous calculation finished", async () => {
    axios.mockResolvedValueOnce({ data: saved }).mockResolvedValueOnce({ data: { ...saved, id: "a2" } });
    const { result } = renderHook(() => useAnalysis("mendelian"), { wrapper });
    await act(async () => result.current.run({}));
    await act(async () => result.current.run({}));
    expect(axios).toHaveBeenCalledTimes(2);
    expect(result.current.analysis.id).toBe("a2");
  });

  it("shows the server's localized error and clears loading", async () => {
    axios.mockRejectedValueOnce({ response: { data: { detail: { code: "invalid_genotype", message: "Invalid genotype for this inheritance mode." } } } });
    const { result } = renderHook(() => useAnalysis("mendelian"), { wrapper });
    await act(async () => result.current.run({}));
    expect(result.current.error).toBe("Invalid genotype for this inheritance mode.");
    expect(result.current.loading).toBe(false);
    expect(result.current.analysis).toBeNull();
  });

  it("falls back to a generic message on network errors", async () => {
    axios.mockRejectedValueOnce(new Error("offline"));
    const { result } = renderHook(() => useAnalysis("mendelian"), { wrapper });
    await act(async () => result.current.run({}));
    expect(result.current.error).toBe("Something went wrong. Please try again.");
  });
});
