import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { askQuestion } from '../api';
import CitationCard from './CitationCard';

// Simple markdown renderer (no external library dependency)
function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/^\* (.+)$/gm, '<li>$1</li>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.+)$/gm, (m) => m.startsWith('<') ? m : `<p>${m}</p>`)
    .replace(/<p><\/p>/g, '');
}

const SAMPLE_QUESTIONS = [
  "Explain dynamic programming with examples",
  "How does a hash map work internally?",
  "Design a URL shortener like Bit.ly",
  "What are Amazon's Leadership Principles?",
  "Explain virtual memory and paging in OS",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (query = input.trim()) => {
    if (!query || loading) return;

    const userMsg = { role: 'user', content: query, id: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await askQuestion(query, sessionId);
      const aiMsg = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        hallucination: data.hallucination_detected,
        correction: data.correction_applied,
        quality: data.retrieval_quality,
        confidence: data.confidence_score,
        rewritten: data.rewritten_query !== query ? data.rewritten_query : null,
        steps: data.steps_taken,
        topic: data.topics,
        id: Date.now() + 1,
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: `Error: ${err.response?.data?.detail || err.message || 'Request failed'}`,
        id: Date.now() + 1,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full py-16 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center mb-6 shadow-lg shadow-brand-500/30">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">PlacementPrep AI</h2>
            <p className="text-gray-400 mb-8 text-center max-w-md">
              Ask anything about DSA, System Design, OS, DBMS, CN, OOP, or Behavioral interviews.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="glass-card-hover p-3 text-left text-sm text-gray-300 hover:text-white transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`animate-slide-up ${msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
            {msg.role === 'user' ? (
              <div className="max-w-2xl">
                <div className="bg-brand-600/30 border border-brand-500/30 rounded-2xl rounded-br-md px-4 py-3 text-white">
                  {msg.content}
                </div>
              </div>
            ) : msg.role === 'error' ? (
              <div className="max-w-2xl glass-card p-4 border-red-500/30">
                <div className="flex items-center gap-2 text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  <span>{msg.content}</span>
                </div>
              </div>
            ) : (
              <div className="max-w-3xl w-full space-y-3">
                {/* Metadata badges */}
                <div className="flex flex-wrap items-center gap-2">
                  {msg.topic && (
                    <span className="badge bg-brand-600/30 text-brand-300 border border-brand-500/30">
                      {msg.topic}
                    </span>
                  )}
                  <span className={`badge ${
                    msg.quality === 'CORRECT' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                    msg.quality === 'AMBIGUOUS' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                    'bg-red-500/20 text-red-300 border border-red-500/30'
                  }`}>
                    {msg.quality}
                  </span>
                  {msg.confidence != null && (
                    <span className="badge bg-white/10 text-gray-300 border border-white/10">
                      {Math.round(msg.confidence * 100)}% confidence
                    </span>
                  )}
                  {msg.hallucination && (
                    <span className="badge bg-orange-500/20 text-orange-300 border border-orange-500/30">
                      <AlertTriangle className="w-3 h-3" /> Corrected
                    </span>
                  )}
                </div>

                {/* Rewritten query hint */}
                {msg.rewritten && (
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <RefreshCw className="w-3 h-3" />
                    <span>Query optimized: "{msg.rewritten}"</span>
                  </div>
                )}

                {/* Answer */}
                <div className="glass-card p-5">
                  <div
                    className="prose-dark"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                  />
                </div>

                {/* Citations */}
                {msg.citations?.length > 0 && (
                  <CitationCard citations={msg.citations} />
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-fade-in">
            <div className="glass-card px-5 py-4 flex items-center gap-3">
              <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />
              <span className="text-gray-400 text-sm">Thinking through CRAG pipeline…</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="glass-card p-3 flex items-end gap-3">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about DSA, System Design, OS, DBMS, OOP, Behavioral…"
            rows={1}
            className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none text-sm leading-relaxed"
            style={{ maxHeight: '120px', overflowY: 'auto' }}
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="btn-primary !px-4 !py-2.5 rounded-lg flex items-center gap-2 flex-shrink-0"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
        <p className="text-center text-xs text-gray-600 mt-2">
          Powered by CRAG • Hybrid Retrieval • Hallucination Detection
        </p>
      </div>
    </div>
  );
}
