import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import CareerExplorer from "./pages/CareerExplorer";
import CareerDetails from "./pages/CareerDetails";
import JobSearch from "./pages/JobSearch";
import SkillsAnalysis from "./pages/SkillsAnalysis";
import AIAssistant from "./pages/AIAssistant";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="careers" element={<CareerExplorer />} />
            <Route path="careers/:id" element={<CareerDetails />} />
            <Route path="jobs" element={<JobSearch />} />
            <Route path="skills" element={<SkillsAnalysis />} />
            <Route path="assistant" element={<AIAssistant />} />
            {/* Placeholder routes - to be implemented */}
            <Route path="pathways" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Student Pathways - Coming Soon</div>} />
            <Route path="applications" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Applications - Coming Soon</div>} />
            <Route path="learning" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Learning Hub - Coming Soon</div>} />
            <Route path="achievements" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Achievements - Coming Soon</div>} />
            <Route path="analytics" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Analytics - Coming Soon</div>} />
            <Route path="settings" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Settings - Coming Soon</div>} />
            <Route path="help" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Help & Support - Coming Soon</div>} />
            <Route path="profile" element={<div className="flex items-center justify-center min-h-[400px] text-muted-foreground">Profile - Coming Soon</div>} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;