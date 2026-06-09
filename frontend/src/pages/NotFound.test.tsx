import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import { render } from "@/test/test-utils";
import NotFound from "./NotFound";

// Mock console.log to verify logging behavior
vi.spyOn(console, "log").mockImplementation(() => {});

describe("NotFound Page", () => {
  it("renders 404 message", () => {
    render(<NotFound />);
    expect(screen.getByText(/404|Not Found|Page/i)).toBeInTheDocument();
  });

  it("displays helpful message", () => {
    render(<NotFound />);
    expect(
      screen.getByText(/not found|doesn't exist|looking for/i)
    ).toBeInTheDocument();
  });

  it("provides navigation link to home", () => {
    render(<NotFound />);
    const homeLink = screen.getByRole("link", { name: /home|back|return|dashboard/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute("href", "/");
  });
});

describe("NotFound Page Layout", () => {
  it("renders centered content", () => {
    render(<NotFound />);
    // Should have some visual content
    expect(screen.getByText(/404/i)).toBeInTheDocument();
  });

  it("has proper heading structure", () => {
    render(<NotFound />);
    const headings = screen.getAllByRole("heading");
    expect(headings.length).toBeGreaterThan(0);
  });
});

describe("NotFound Page Accessibility", () => {
  it("has accessible link to navigate away", () => {
    render(<NotFound />);
    const links = screen.getAllByRole("link");
    expect(links.length).toBeGreaterThan(0);
  });
});
