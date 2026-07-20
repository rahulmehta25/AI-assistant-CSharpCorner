import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

const pageVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -4 },
};

const pageTransition = {
  duration: 0.22,
  ease: [0.4, 0, 0.2, 1] as [number, number, number, number],
};

export const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const toggleSidebar = () => setSidebarOpen((v) => !v);
  const closeSidebar  = () => setSidebarOpen(false);

  return (
    <div id="layout-root" className="min-h-screen bg-background">
      {/* Hero ambient glow — subtle radial behind content */}
      <div
        id="layout-glow"
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -15%, hsl(213 93% 60% / 0.07) 0%, transparent 65%)',
        }}
      />

      <Header onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen} />

      <div id="layout-body" className="flex">
        <Sidebar open={sidebarOpen} onClose={closeSidebar} />

        <main
          id="layout-main"
          className="relative z-10 flex-1 lg:ml-64 min-h-[calc(100vh-4rem)]"
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={pageTransition}
              id="page-container"
              className="container mx-auto p-4 lg:p-6"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};
