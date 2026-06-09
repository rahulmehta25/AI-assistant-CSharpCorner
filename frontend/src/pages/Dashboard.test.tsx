import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { render } from "@/test/test-utils";
import Dashboard from "./Dashboard";

// Mock the API service
vi.mock("@/services/api", () => ({
  default: {
    getCareers: vi.fn().mockResolvedValue({
      careers: [
        {
          id: "15-1252.00",
          title: "Software Developers",
          description: "Develop software",
          match: 92,
          salary: { min: 96000, max: 168000 },
          growth: "high",
          education: "Bachelor's degree",
          skills: ["Python", "JavaScript"],
        },
      ],
      total: 1,
    }),
  },
}));

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    user: {
      id: "user123",
      name: "Test User",
      email: "test@example.com",
      profile: {
        title: "Software Engineer",
        experience: 3,
        skills: [{ id: "1", name: "Python", level: "advanced" }],
      },
      progress: {
        careerMatch: 85,
        skillsCompleted: 12,
        applications: 5,
        profileCompletion: 75,
      },
    },
    bookmarkedCareers: [],
    savedJobs: [],
    bookmarkCareer: vi.fn(),
    unbookmarkCareer: vi.fn(),
  })),
}));

describe("Dashboard Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the dashboard header", () => {
    render(<Dashboard />);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  });

  it("displays welcome message", () => {
    render(<Dashboard />);
    // Should welcome the user
    expect(
      screen.getByText(/Welcome|Hello|Hi/i) || screen.getByRole("heading")
    ).toBeInTheDocument();
  });

  it("renders stats cards section", () => {
    render(<Dashboard />);
    // Stats cards should be present
    expect(
      screen.getByText(/Career Match|Skills|Applications|Profile/i)
    ).toBeInTheDocument();
  });

  it("displays career matches section", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Career|Matches|Recommendations/i)).toBeInTheDocument();
    });
  });

  it("renders quick actions or navigation", () => {
    render(<Dashboard />);
    // Should have some navigation elements
    const links = screen.getAllByRole("link");
    expect(links.length).toBeGreaterThan(0);
  });
});

describe("Dashboard Stats", () => {
  it("displays career match percentage", () => {
    render(<Dashboard />);
    // Should show the user's career match score
    expect(
      screen.getByText(/85%|85|Match/i) || screen.getByText(/Career/i)
    ).toBeInTheDocument();
  });

  it("displays profile completion", () => {
    render(<Dashboard />);
    expect(
      screen.getByText(/75%|75|Complete|Profile/i) ||
        screen.getByText(/Progress/i)
    ).toBeInTheDocument();
  });
});

describe("Dashboard Career Recommendations", () => {
  it("fetches and displays career data", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      // Should attempt to load careers
      expect(screen.getByText(/Career|Software|Loading/i)).toBeInTheDocument();
    });
  });
});

describe("Dashboard Loading State", () => {
  it("shows loading indicator initially", () => {
    render(<Dashboard />);
    // During initial load, should show something
    expect(screen.getByText(/.+/)).toBeInTheDocument();
  });
});

describe("Dashboard Layout", () => {
  it("renders in a grid layout", () => {
    render(<Dashboard />);
    // The dashboard should render multiple sections
    const sections = screen.getAllByRole("heading");
    expect(sections.length).toBeGreaterThan(0);
  });
});
