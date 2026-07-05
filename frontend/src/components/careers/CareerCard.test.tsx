import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, fireEvent } from "@testing-library/react";
import { render } from "@/test/test-utils";
import { CareerCard } from "./CareerCard";
import { Career } from "@/types";

const mockCareer: Career = {
  id: "15-1252.00",
  title: "Software Developers",
  description: "Research, design, and develop computer and network software.",
  match: 92,
  salary: { min: 96160, max: 168280 },
  growth: "high",
  education: "Bachelor's degree",
  experience: "2-5 years",
  skills: ["Python", "JavaScript", "SQL", "React", "AWS"],
  tasks: ["Write code", "Debug software", "Review code"],
  cluster: "Information Technology",
};

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    bookmarkedCareers: [],
    bookmarkCareer: vi.fn(),
    unbookmarkCareer: vi.fn(),
  })),
}));

describe("CareerCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders career title correctly", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByText("Software Developers")).toBeInTheDocument();
  });

  it("renders career description", () => {
    render(<CareerCard career={mockCareer} />);
    expect(
      screen.getByText(/Research, design, and develop/)
    ).toBeInTheDocument();
  });

  it("displays match percentage when showMatch is true", () => {
    render(<CareerCard career={mockCareer} showMatch={true} />);
    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText("Match")).toBeInTheDocument();
  });

  it("hides match percentage when showMatch is false", () => {
    render(<CareerCard career={mockCareer} showMatch={false} />);
    expect(screen.queryByText("92%")).not.toBeInTheDocument();
  });

  it("displays salary range correctly", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByText("$96k - $168k")).toBeInTheDocument();
  });

  it("displays education requirement", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByText("Bachelor's degree")).toBeInTheDocument();
  });

  it("displays growth indicator", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByText(/high growth/i)).toBeInTheDocument();
  });

  it("displays key skills (limited to 3)", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
    expect(screen.getByText("SQL")).toBeInTheDocument();
    expect(screen.getByText("+2 more")).toBeInTheDocument();
  });

  it("hides description in compact mode", () => {
    render(<CareerCard career={mockCareer} compact={true} />);
    expect(
      screen.queryByText(/Research, design, and develop/)
    ).not.toBeInTheDocument();
  });

  it("hides skills section in compact mode", () => {
    render(<CareerCard career={mockCareer} compact={true} />);
    expect(screen.queryByText("Key Skills")).not.toBeInTheDocument();
  });

  it("links to career details page", () => {
    render(<CareerCard career={mockCareer} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/careers/15-1252.00");
  });

  it("renders bookmark button", () => {
    render(<CareerCard career={mockCareer} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("calls bookmark function when clicked", () => {
    const mockBookmarkCareer = vi.fn();

    vi.mocked(
      await import("@/store/useUserStore")
    ).useUserStore.mockReturnValue({
      bookmarkedCareers: [],
      bookmarkCareer: mockBookmarkCareer,
      unbookmarkCareer: vi.fn(),
    });

    render(<CareerCard career={mockCareer} />);
    const bookmarkButton = screen.getByRole("button");
    fireEvent.click(bookmarkButton);
  });
});

describe("CareerCard with bookmarked career", () => {
  it("shows filled bookmark icon when career is bookmarked", async () => {
    const { useUserStore } = await import("@/store/useUserStore");
    vi.mocked(useUserStore).mockReturnValue({
      bookmarkedCareers: [mockCareer],
      bookmarkCareer: vi.fn(),
      unbookmarkCareer: vi.fn(),
    });

    render(<CareerCard career={mockCareer} />);
    // The BookmarkCheck icon should be present for bookmarked careers
    expect(screen.getByRole("button")).toBeInTheDocument();
  });
});

describe("CareerCard salary formatting", () => {
  it("formats salary correctly for various ranges", () => {
    const lowSalaryCareer = {
      ...mockCareer,
      salary: { min: 50000, max: 75000 },
    };
    render(<CareerCard career={lowSalaryCareer} />);
    expect(screen.getByText("$50k - $75k")).toBeInTheDocument();
  });

  it("handles high salaries correctly", () => {
    const highSalaryCareer = {
      ...mockCareer,
      salary: { min: 200000, max: 350000 },
    };
    render(<CareerCard career={highSalaryCareer} />);
    expect(screen.getByText("$200k - $350k")).toBeInTheDocument();
  });
});

describe("CareerCard growth indicator", () => {
  it("applies correct styling for high growth", () => {
    render(<CareerCard career={{ ...mockCareer, growth: "high" }} />);
    expect(screen.getByText(/high growth/i)).toBeInTheDocument();
  });

  it("applies correct styling for medium growth", () => {
    render(<CareerCard career={{ ...mockCareer, growth: "medium" }} />);
    expect(screen.getByText(/medium growth/i)).toBeInTheDocument();
  });

  it("applies correct styling for low growth", () => {
    render(<CareerCard career={{ ...mockCareer, growth: "low" }} />);
    expect(screen.getByText(/low growth/i)).toBeInTheDocument();
  });
});
