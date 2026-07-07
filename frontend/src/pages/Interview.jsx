import { useState } from 'react';
import CompanySelector from '../components/CompanySelector';
import InterviewRoom from '../components/InterviewRoom';

export default function Interview() {
  const [selectedCompany, setSelectedCompany] = useState(null);

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-white/10 flex-shrink-0">
        <h1 className="text-xl font-bold text-white tracking-tight">Interview Simulator</h1>
        <p className="text-xs text-gray-400 font-medium mt-1">Company-specific mock interviews</p>
      </header>
      
      <main className="flex-1 overflow-y-auto p-6">
        {!selectedCompany ? (
          <div className="max-w-6xl mx-auto py-6">
            <CompanySelector onSelect={setSelectedCompany} />
          </div>
        ) : (
          <InterviewRoom 
            company={selectedCompany} 
            onExit={() => setSelectedCompany(null)} 
          />
        )}
      </main>
    </div>
  );
}
