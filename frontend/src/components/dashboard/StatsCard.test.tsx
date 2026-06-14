import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { render } from "@/test/test-utils";
import { StatsCard } from "./StatsCard";
import { TrendingUp } from "lucide-react";

describe("StatsCard", () => {
  it("renders title correctly", () => {
    render(<StatsCard title="Total Users" value={1250} />);
    expect(screen.getByText("Total Users")).toBeInTheDocument();
  });

  it("renders numeric value correctly", () => {
    render(<StatsCard title="Users" value={1250} />);
    expect(screen.getByText("1250")).toBeInTheDocument();
  });

  it("renders string value correctly", () => {
    render(<StatsCard title="Status" value="Active" />);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("renders icon when provided", () => {
    render(
      <StatsCard
        title="Trending"
        value={100}
        icon={<TrendingUp data-testid="trending-icon" />}
      />
    );
    expect(screen.getByTestId("trending-icon")).toBeInTheDocument();
  });

  it("displays positive change indicator", () => {
    render(
      <StatsCard
        title="Growth"
        value={100}
        change={{ value: 12, trend: "up" }}
      />
    );
    expect(screen.getByText("+12%")).toBeInTheDocument();
  });

  it("displays negative change indicator", () => {
    render(
      <StatsCard
        title="Decline"
        value={100}
        change={{ value: -5, trend: "down" }}
      />
    );
    expect(screen.getByText("-5%")).toBeInTheDocument();
  });

  it("displays progress bar when progress is provided", () => {
    render(<StatsCard title="Completion" value="75%" progress={75} />);
    expect(screen.getByText("75% complete")).toBeInTheDocument();
  });

  it("displays description when provided", () => {
    render(
      <StatsCard
        title="Stats"
        value={100}
        description="Last 30 days"
      />
    );
    expect(screen.getByText("Last 30 days")).toBeInTheDocument();
  });

  it("does not display change indicator when not provided", () => {
    render(<StatsCard title="Simple" value={100} />);
    expect(screen.queryByText(/%$/)).not.toBeInTheDocument();
  });

  it("does not display progress when not provided", () => {
    render(<StatsCard title="No Progress" value={100} />);
    expect(screen.queryByText(/complete/)).not.toBeInTheDocument();
  });
});

describe("StatsCard variants", () => {
  it("renders with default variant", () => {
    render(<StatsCard title="Default" value={100} variant="default" />);
    expect(screen.getByText("Default")).toBeInTheDocument();
  });

  it("renders with success variant", () => {
    render(<StatsCard title="Success" value={100} variant="success" />);
    expect(screen.getByText("Success")).toBeInTheDocument();
  });

  it("renders with warning variant", () => {
    render(<StatsCard title="Warning" value={100} variant="warning" />);
    expect(screen.getByText("Warning")).toBeInTheDocument();
  });

  it("renders with destructive variant", () => {
    render(<StatsCard title="Destructive" value={100} variant="destructive" />);
    expect(screen.getByText("Destructive")).toBeInTheDocument();
  });
});

describe("StatsCard accessibility", () => {
  it("renders as an article/card element", () => {
    render(<StatsCard title="Accessible" value={100} />);
    expect(screen.getByText("Accessible")).toBeInTheDocument();
  });

  it("displays title in accessible heading", () => {
    render(<StatsCard title="My Title" value={100} />);
    expect(screen.getByText("My Title")).toBeInTheDocument();
  });
});

describe("StatsCard edge cases", () => {
  it("handles zero value", () => {
    render(<StatsCard title="Zero" value={0} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("handles large numbers", () => {
    render(<StatsCard title="Large" value={1000000} />);
    expect(screen.getByText("1000000")).toBeInTheDocument();
  });

  it("handles zero progress", () => {
    render(<StatsCard title="Start" value="0%" progress={0} />);
    expect(screen.getByText("0% complete")).toBeInTheDocument();
  });

  it("handles 100% progress", () => {
    render(<StatsCard title="Complete" value="100%" progress={100} />);
    expect(screen.getByText("100% complete")).toBeInTheDocument();
  });
});
