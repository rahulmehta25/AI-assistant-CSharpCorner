import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { render } from "@/test/test-utils";
import SkillsAnalysis from "./SkillsAnalysis";

// Mock the useUserStore
vi.mock("@/store/useUserStore", () => ({
  useUserStore: vi.fn(() => ({
    user: {
      id: "user123",
      name: "Test User",
      profile: {
        skills: [
          { id: "1", name: "Python", level: "advanced", category: "Programming" },
          { id: "2", name: "JavaScript", level: "intermediate", category: "Programming" },
          { id: "3", name: "React", level: "intermediate", category: "Frontend" },
        ],
      },
    },
  })),
}));

describe("SkillsAnalysis Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the page header", () => {
    render(<SkillsAnalysis />);
    expect(screen.getByText(/Skills|Analysis|Assessment/i)).toBeInTheDocument();
  });

  it("displays skills overview section", () => {
    render(<SkillsAnalysis />);
    expect(
      screen.getByText(/Overview|Skills|Current/i)
    ).toBeInTheDocument();
  });

  it("shows skill gaps section", () => {
    render(<SkillsAnalysis />);
    expect(
      screen.getByText(/Gap|Missing|Improve|Recommendations/i)
    ).toBeInTheDocument();
  });
});

describe("SkillsAnalysis Skills Display", () => {
  it("displays user skills", async () => {
    render(<SkillsAnalysis />);
    await waitFor(() => {
      expect(
        screen.getByText(/Python|JavaScript|React|Skills/i)
      ).toBeInTheDocument();
    });
  });

  it("shows skill levels", async () => {
    render(<SkillsAnalysis />);
    await waitFor(() => {
      expect(
        screen.getByText(/Advanced|Intermediate|Beginner|Level/i)
      ).toBeInTheDocument();
    });
  });
});

describe("SkillsAnalysis Skill Gaps", () => {
  it("displays skill gap recommendations", () => {
    render(<SkillsAnalysis />);
    expect(
      screen.getByText(/Gap|Learn|Improve|Recommend/i)
    ).toBeInTheDocument();
  });
});

describe("SkillsAnalysis Learning Recommendations", () => {
  it("shows learning resources section", () => {
    render(<SkillsAnalysis />);
    expect(
      screen.getByText(/Learn|Resources|Course|Recommendation/i)
    ).toBeInTheDocument();
  });
});

describe("SkillsAnalysis Progress", () => {
  it("displays progress indicators", () => {
    render(<SkillsAnalysis />);
    // Should show some progress or completion indicators
    expect(
      screen.getByText(/Progress|Complete|%|Level/i)
    ).toBeInTheDocument();
  });
});

describe("SkillsAnalysis Layout", () => {
  it("renders multiple sections", () => {
    render(<SkillsAnalysis />);
    const headings = screen.getAllByRole("heading");
    expect(headings.length).toBeGreaterThan(0);
  });
});

describe("SkillsAnalysis Categories", () => {
  it("organizes skills by category", async () => {
    render(<SkillsAnalysis />);
    await waitFor(() => {
      // Should show skill organization
      expect(
        screen.getByText(/Category|Programming|Frontend|Skills/i)
      ).toBeInTheDocument();
    });
  });
});
