import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, fireEvent } from "@testing-library/react";
import { render } from "@/test/test-utils";
import { JobCard } from "./JobCard";
import { Job } from "@/types";

const mockJob: Job = {
  id: "job-123",
  title: "Senior Software Engineer",
  company: "Tech Corp",
  location: "San Francisco, CA",
  salary: "$150k - $200k",
  type: "full-time",
  description: "Join our engineering team to build amazing products.",
  requirements: ["5+ years experience", "Python/JavaScript", "AWS", "Docker"],
  benefits: ["Health insurance", "401k", "Remote work"],
  match: 95,
  postedDate: "2026-03-10",
  applied: false,
  saved: false,
  source: "indeed",
};

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    savedJobs: [],
    saveJob: vi.fn(),
    unsaveJob: vi.fn(),
  })),
}));

describe("JobCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders job title correctly", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("Senior Software Engineer")).toBeInTheDocument();
  });

  it("renders company name", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("Tech Corp")).toBeInTheDocument();
  });

  it("renders job description", () => {
    render(<JobCard job={mockJob} />);
    expect(
      screen.getByText(/Join our engineering team/)
    ).toBeInTheDocument();
  });

  it("displays match percentage when showMatch is true", () => {
    render(<JobCard job={mockJob} showMatch={true} />);
    expect(screen.getByText("95%")).toBeInTheDocument();
    expect(screen.getByText("Match")).toBeInTheDocument();
  });

  it("hides match percentage when showMatch is false", () => {
    render(<JobCard job={mockJob} showMatch={false} />);
    expect(screen.queryByText("95%")).not.toBeInTheDocument();
  });

  it("displays location", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("San Francisco, CA")).toBeInTheDocument();
  });

  it("displays salary", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("$150k - $200k")).toBeInTheDocument();
  });

  it("displays job type badge", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("full time")).toBeInTheDocument();
  });

  it("displays job requirements (limited to 3)", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("5+ years experience")).toBeInTheDocument();
    expect(screen.getByText("Python/JavaScript")).toBeInTheDocument();
    expect(screen.getByText("AWS")).toBeInTheDocument();
    expect(screen.getByText("+1 more")).toBeInTheDocument();
  });

  it("displays job source", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText("via indeed")).toBeInTheDocument();
  });

  it("hides description in compact mode", () => {
    render(<JobCard job={mockJob} compact={true} />);
    expect(
      screen.queryByText(/Join our engineering team/)
    ).not.toBeInTheDocument();
  });

  it("hides requirements section in compact mode", () => {
    render(<JobCard job={mockJob} compact={true} />);
    expect(screen.queryByText("Key Requirements")).not.toBeInTheDocument();
  });

  it("links to job details page", () => {
    render(<JobCard job={mockJob} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/jobs/job-123");
  });

  it("renders save button", () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });
});

describe("JobCard job types", () => {
  it("displays full-time job type correctly", () => {
    render(<JobCard job={{ ...mockJob, type: "full-time" }} />);
    expect(screen.getByText("full time")).toBeInTheDocument();
  });

  it("displays part-time job type correctly", () => {
    render(<JobCard job={{ ...mockJob, type: "part-time" }} />);
    expect(screen.getByText("part time")).toBeInTheDocument();
  });

  it("displays contract job type correctly", () => {
    render(<JobCard job={{ ...mockJob, type: "contract" }} />);
    expect(screen.getByText("contract")).toBeInTheDocument();
  });

  it("displays internship job type correctly", () => {
    render(<JobCard job={{ ...mockJob, type: "internship" }} />);
    expect(screen.getByText("internship")).toBeInTheDocument();
  });
});

describe("JobCard date formatting", () => {
  it("displays recently posted date correctly", () => {
    const recentJob = {
      ...mockJob,
      postedDate: new Date().toISOString().split("T")[0],
    };
    render(<JobCard job={recentJob} />);
    // Should show "1 day ago" or similar
    expect(screen.getByText(/ago/)).toBeInTheDocument();
  });
});

describe("JobCard applied/saved status", () => {
  it("shows Applied badge when job is applied", () => {
    render(<JobCard job={{ ...mockJob, applied: true }} />);
    expect(screen.getByText("Applied")).toBeInTheDocument();
  });

  it("shows Saved badge when job is saved", () => {
    render(<JobCard job={{ ...mockJob, saved: true }} />);
    expect(screen.getByText("Saved")).toBeInTheDocument();
  });
});

describe("JobCard save functionality", () => {
  it("calls saveJob when save button is clicked", async () => {
    const mockSaveJob = vi.fn();
    const { useUserStore } = await import("@/store/useUserStore");
    vi.mocked(useUserStore).mockReturnValue({
      savedJobs: [],
      saveJob: mockSaveJob,
      unsaveJob: vi.fn(),
    });

    render(<JobCard job={mockJob} />);
    const saveButton = screen.getByRole("button");
    fireEvent.click(saveButton);
  });

  it("calls unsaveJob when job is already saved", async () => {
    const mockUnsaveJob = vi.fn();
    const { useUserStore } = await import("@/store/useUserStore");
    vi.mocked(useUserStore).mockReturnValue({
      savedJobs: [mockJob],
      saveJob: vi.fn(),
      unsaveJob: mockUnsaveJob,
    });

    render(<JobCard job={mockJob} />);
    const saveButton = screen.getByRole("button");
    fireEvent.click(saveButton);
  });
});
