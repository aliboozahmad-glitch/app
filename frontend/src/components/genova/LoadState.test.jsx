import { fireEvent, render, screen } from "@testing-library/react";
import { LanguageProvider } from "@/i18n/LanguageContext";
import { LoadState } from "./LoadState";

const renderState = (state) =>
  render(
    <LanguageProvider>
      <LoadState state={{ retry: jest.fn(), ...state }} testId="catalog">
        {(data) => <p data-testid="content">{data.name}</p>}
      </LoadState>
    </LanguageProvider>,
  );

beforeEach(() => localStorage.setItem("genova-lang", "en"));

describe("LoadState", () => {
  it("shows a loading indicator before data arrives", () => {
    renderState({ data: null, loading: true, error: false });
    expect(screen.getByTestId("catalog-loading")).toHaveTextContent("Loading");
    expect(screen.queryByTestId("content")).toBeNull();
  });

  it("shows an error box with Retry when the first load fails", () => {
    const retry = jest.fn();
    renderState({ data: null, loading: false, error: true, retry });
    expect(screen.getByTestId("catalog-error")).toHaveTextContent("Could not load data.");
    fireEvent.click(screen.getByTestId("catalog-retry"));
    expect(retry).toHaveBeenCalledTimes(1);
    expect(screen.queryByTestId("content")).toBeNull();
  });

  it("renders content when data is loaded", () => {
    renderState({ data: { name: "Beta-thalassaemia" }, loading: false, error: false });
    expect(screen.getByTestId("content")).toHaveTextContent("Beta-thalassaemia");
    expect(screen.queryByTestId("catalog-error")).toBeNull();
  });

  it("keeps earlier data visible with an inline error after a failed refetch", () => {
    renderState({ data: { name: "Cystic fibrosis" }, loading: false, error: true });
    expect(screen.getByTestId("content")).toHaveTextContent("Cystic fibrosis");
    expect(screen.getByTestId("catalog-error")).toBeInTheDocument();
  });

  it("is translated (Arabic)", () => {
    localStorage.setItem("genova-lang", "ar");
    renderState({ data: null, loading: false, error: true });
    expect(screen.getByTestId("catalog-retry")).toHaveTextContent("إعادة المحاولة");
  });
});
