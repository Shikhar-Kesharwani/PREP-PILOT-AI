import ChatInterface from '../components/ChatInterface';

export default function Home() {
  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-white/10 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">CRAG Tutor</h1>
          <p className="text-xs text-brand-400 font-medium">PlacementPrep AI</p>
        </div>
        <div className="text-xs text-gray-500 font-medium px-3 py-1 bg-white/5 rounded-full border border-white/10">
          Powered by Llama 3 & ChromaDB
        </div>
      </header>
      
      <main className="flex-1 overflow-hidden relative">
        <ChatInterface />
      </main>
    </div>
  );
}
