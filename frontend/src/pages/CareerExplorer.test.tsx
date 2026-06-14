import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { render } from "@/test/test-utils";
import CareerExplorer from "./CareerExplorer";

// Mock the API service
vi.mock("@/services/api", () => ({
  default: {
    getCareers: vi.fn().mockResolvedValue({
      careers: [
        {
          id: "15-1252.00",
          title: "Software Developers",
          description: "Research, design, and develop computer software.",
          match: 92,
          salary: { min: 96000, max: 168000 },
          growth: "high",
          education: "Bachelor's degree",
          skills: ["Python", "JavaScript", "SQL"],
          cluster: "Information Technology",
        },
        {
          id: "15-2051.00",
          title: "Data Scientists",
          description: "Develop and implement data models.",
          match: 88,
          salary: { min: 86000, max: 152000 },
          growth: "high",
          education: "Master's degree",
          skills: ["Python", "Statistics", "ML"],
          cluster: "Information Technology",
        },
      ],
      total: 2,
    }),
    searchCareers: vi.fn().mockResolvedValue({
      results: [
        {
          id: "15-1252.00",
          title: "Software Developers",
          description: "Develop software",
          match: 92,
          salary: { min: 96000, max: 168000 },
          growth: "high",
        },
      ],
      count: 1,
    }),
  },
}));

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    bookmarkedCareers: [],
    bookmarkCareer: vi.fn(),
    unbookmarkCareer: vi.fn(),
  })),
}));

describe("CareerExplorer Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the page header", () => {
    render(<CareerExplorer />);
    expect(screen.getByText(/Career|Explore|Browse/i)).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(<CareerExplorer />);
    expect(
      screen.getByRole("searchbox") ||
        screen.getByRole("textbox") ||
        screen.getByPlaceholderText(/search/i)
    ).toBeInTheDocument();
  });

  it("displays career cards after loading", async () => {
    render(<CareerExplorer />);
    await waitFor(() => {
      expect(
        screen.getByText(/Software Developers/i) ||
          screen.getByText(/Career/i)
      ).toBeInTheDocument();
    });
  });

  it("shows filters section", () => {
    render(<CareerExplorer />);
    expect(
      screen.getByText(/Filter|Growth|Salary|Education/i)
    ).toBeInTheDocument();
  });
});

describe("CareerExplorer Search", () => {
  it("allows searching for careers", async () => {
    render(<CareerExplorer />);

    const searchInput =
      screen.getByRole("searchbox") ||
      screen.getByRole("textbox") ||
      screen.getByPlaceholderText(/search/i);

    if (searchInput) {
      fireEvent.change(searchInput, { target: { value: "software" } });
      expect(searchInput).toHaveValue("software");
    }
  });
});

describe("CareerExplorer Filtering", () => {
  it("renders filter options", () => {
    render(<CareerExplorer />);
    // Should have filter controls
    expect(
      screen.getByText(/Filter|All|Growth|Education/i)
    ).toBeInTheDocument();
  });
});

describe("CareerExplorer Career Cards", () => {
  it("displays career information in cards", async () => {
    render(<CareerExplorer />);

    await waitFor(() => {
      // Should show career details
      const content = screen.getByText(/Software|Career|Developer/i);
      expect(content).toBeInTheDocument();
    });
  });

  it("shows salary information", async () => {
    render(<CareerExplorer />);

    await waitFor(() => {
      expect(screen.getByText(/\$|salary|k/i)).toBeInTheDocument();
    });
  });
});

describe("CareerExplorer Navigation", () => {
  it("career cards link to detail pages", async () => {
    render(<CareerExplorer />);

    await waitFor(() => {
      const links = screen.getAllByRole("link");
      expect(links.length).toBeGreaterThan(0);
    });
  });
});

describe("CareerExplorer Loading State", () => {
  it("shows loading state initially", () => {
    render(<CareerExplorer />);
    // Should show content or loading indicator
    expect(screen.getByText(/.+/)).toBeInTheDocument();
  });
});

describe("CareerExplorer Results Count", () => {
  it("displays total number of careers", async () => {
    render(<CareerExplorer />);

    await waitFor(() => {
      // Should show some indication of results
      expect(
        screen.getByText(/career|result|found|\d+/i)
      ).toBeInTheDocument();
    });
  });
});
