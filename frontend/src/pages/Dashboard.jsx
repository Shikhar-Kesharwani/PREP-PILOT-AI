import ProgressDashboard from '../components/ProgressDashboard';

export default function Dashboard() {
  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-white/10 flex-shrink-0">
        <h1 className="text-xl font-bold text-white tracking-tight">Analytics Dashboard</h1>
        <p className="text-xs text-gray-400 font-medium mt-1">Track your progress and mastery</p>
      </header>
      
      <main className="flex-1 overflow-y-auto p-6">
        <ProgressDashboard userId={1} />
      </main>
    </div>
  );
}
