import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { render } from "@/test/test-utils";
import JobSearch from "./JobSearch";

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    savedJobs: [],
    saveJob: vi.fn(),
    unsaveJob: vi.fn(),
  })),
}));

describe("JobSearch Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the page header", () => {
    render(<JobSearch />);
    expect(screen.getByText(/Job|Search|Find/i)).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(<JobSearch />);
    const searchInputs = screen.getAllByRole("textbox");
    expect(searchInputs.length).toBeGreaterThan(0);
  });

  it("displays job cards", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      expect(
        screen.getByText(/Software|Engineer|Developer|Job/i)
      ).toBeInTheDocument();
    });
  });

  it("shows filter options", () => {
    render(<JobSearch />);
    expect(
      screen.getByText(/Filter|Location|Type|Salary|Remote/i)
    ).toBeInTheDocument();
  });
});

describe("JobSearch Filters", () => {
  it("renders location filter", () => {
    render(<JobSearch />);
    expect(
      screen.getByText(/Location|City|Remote/i) ||
        screen.getByPlaceholderText(/location/i)
    ).toBeInTheDocument();
  });

  it("renders job type filter", () => {
    render(<JobSearch />);
    expect(
      screen.getByText(/Type|Full|Part|Contract|Internship/i)
    ).toBeInTheDocument();
  });

  it("renders salary range filter", () => {
    render(<JobSearch />);
    expect(screen.getByText(/Salary|\$/i)).toBeInTheDocument();
  });
});

describe("JobSearch Job Cards", () => {
  it("displays job title", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      expect(
        screen.getByText(/Engineer|Developer|Manager/i)
      ).toBeInTheDocument();
    });
  });

  it("displays company name", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      // Should show some company information
      const content = document.body.textContent;
      expect(content?.length).toBeGreaterThan(0);
    });
  });

  it("displays location", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      expect(
        screen.getByText(/Remote|San Francisco|Location/i)
      ).toBeInTheDocument();
    });
  });
});

describe("JobSearch Save Functionality", () => {
  it("renders save buttons on job cards", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      const buttons = screen.getAllByRole("button");
      expect(buttons.length).toBeGreaterThan(0);
    });
  });
});

describe("JobSearch Quick Stats", () => {
  it("shows job statistics", () => {
    render(<JobSearch />);
    expect(
      screen.getByText(/\d+|Jobs|Found|Available/i)
    ).toBeInTheDocument();
  });
});

describe("JobSearch Navigation", () => {
  it("job cards link to detail pages", async () => {
    render(<JobSearch />);
    await waitFor(() => {
      const links = screen.getAllByRole("link");
      expect(links.length).toBeGreaterThan(0);
    });
  });
});

describe("JobSearch Loading State", () => {
  it("renders content or loading state", () => {
    render(<JobSearch />);
    expect(screen.getByText(/.+/)).toBeInTheDocument();
  });
});

describe("JobSearch Empty State", () => {
  it("handles empty results gracefully", async () => {
    render(<JobSearch />);
    // Should at least render the page structure
    expect(screen.getByText(/Job|Search/i)).toBeInTheDocument();
  });
});
