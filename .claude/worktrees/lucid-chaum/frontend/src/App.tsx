import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import Dashboard from "./pages/Dashboard";
import CareerExplorer from "./pages/CareerExplorer";
import CareerDetails from "./pages/CareerDetails";
import JobSearch from "./pages/JobSearch";
import SkillsAnalysis from "./pages/SkillsAnalysis";
import AIAssistant from "./pages/AIAssistant";
import Pathways from "./pages/Pathways";
import Applications from "./pages/Applications";
import Learning from "./pages/Learning";
import Achievements from "./pages/Achievements";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import Help from "./pages/Help";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
            <Route path="careers" element={<ErrorBoundary><CareerExplorer /></ErrorBoundary>} />
            <Route path="careers/:id" element={<ErrorBoundary><CareerDetails /></ErrorBoundary>} />
            <Route path="jobs" element={<ErrorBoundary><JobSearch /></ErrorBoundary>} />
            <Route path="skills" element={<ErrorBoundary><SkillsAnalysis /></ErrorBoundary>} />
            <Route path="assistant" element={<ErrorBoundary><AIAssistant /></ErrorBoundary>} />
            <Route path="pathways" element={<ErrorBoundary><Pathways /></ErrorBoundary>} />
            <Route path="applications" element={<ErrorBoundary><Applications /></ErrorBoundary>} />
            <Route path="learning" element={<ErrorBoundary><Learning /></ErrorBoundary>} />
            <Route path="achievements" element={<ErrorBoundary><Achievements /></ErrorBoundary>} />
            <Route path="analytics" element={<ErrorBoundary><Analytics /></ErrorBoundary>} />
            <Route path="settings" element={<ErrorBoundary><Settings /></ErrorBoundary>} />
            <Route path="help" element={<ErrorBoundary><Help /></ErrorBoundary>} />
            <Route path="profile" element={<ErrorBoundary><Profile /></ErrorBoundary>} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
