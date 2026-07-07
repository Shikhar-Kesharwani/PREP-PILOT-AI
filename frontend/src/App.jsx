import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { MessageSquare, Briefcase, LayoutDashboard } from 'lucide-react';
import Home from './pages/Home';
import Interview from './pages/Interview';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-surface-900 text-gray-100 font-sans">
        
        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0 bg-surface-800/50 border-r border-white/5 flex flex-col">
          <div className="p-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg shadow-brand-500/20">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">PlacementPrep</h2>
            <p className="text-xs text-brand-400 font-medium mt-1">AI Tutor & Simulator</p>
          </div>

          <nav className="flex-1 px-4 space-y-2 mt-4">
            <NavLink 
              to="/chat" 
              className={({ isActive }) => isActive ? "nav-link-active" : "nav-link"}
            >
              <MessageSquare className="w-5 h-5" />
              CRAG Tutor
            </NavLink>
            <NavLink 
              to="/interview" 
              className={({ isActive }) => isActive ? "nav-link-active" : "nav-link"}
            >
              <Briefcase className="w-5 h-5" />
              Interview Simulator
            </NavLink>
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => isActive ? "nav-link-active" : "nav-link"}
            >
              <LayoutDashboard className="w-5 h-5" />
              Analytics
            </NavLink>
          </nav>

          <div className="p-4 m-4 rounded-xl bg-white/5 border border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-sm font-bold text-white">
                G
              </div>
              <div>
                <p className="text-sm font-medium text-white">Guest User</p>
                <p className="text-xs text-gray-500">Free Tier</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 min-w-0 relative bg-surface-900">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<Home />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
