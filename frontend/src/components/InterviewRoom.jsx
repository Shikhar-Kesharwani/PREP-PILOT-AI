import { useState, useEffect } from 'react';
import { getCompanyQuestion, evaluateAnswer, saveSession } from '../api';
import { Loader2, Play, AlertCircle, CheckCircle, ChevronRight, XCircle } from 'lucide-react';

export default function InterviewRoom({ company, onExit }) {
  const [sessionData, setSessionData] = useState({
    sessionId: crypto.randomUUID(),
    questionsAsked: 0,
    totalScore: 0,
    history: [],
  });

  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const fetchQuestion = async () => {
    setLoading(true);
    setFeedback(null);
    setAnswer('');
    try {
      const prev = sessionData.history.map(h => h.question);
      const res = await getCompanyQuestion(company, prev);
      setCurrentQuestion(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestion();
    // eslint-disable-next-line
  }, []);

  const handleSubmit = async () => {
    if (!answer.trim() || evaluating) return;
    setEvaluating(true);

    try {
      const res = await evaluateAnswer(
        company,
        currentQuestion.question,
        answer,
        currentQuestion.type,
        currentQuestion.expected_points,
        sessionData.sessionId
      );

      setFeedback(res.data);
      setSessionData(prev => ({
        ...prev,
        questionsAsked: prev.questionsAsked + 1,
        totalScore: prev.totalScore + res.data.score,
        history: [...prev.history, currentQuestion.question],
      }));
    } catch (err) {
      console.error(err);
      alert('Evaluation failed. Please try again.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleEndSession = async () => {
    try {
      await saveSession({
        session_id: sessionData.sessionId,
        user_id: 1, // Assume guest user for now
        company: company,
        mode: 'company',
        total_score: sessionData.totalScore / Math.max(1, sessionData.questionsAsked),
        total_questions: sessionData.questionsAsked,
      });
    } catch (e) {
      console.error(e);
    }
    onExit();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-brand-400 animate-spin mb-4" />
        <p className="text-gray-400">Preparing your next question from {company}...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col pt-6">
      <div className="flex items-center justify-between mb-6 pb-6 border-b border-white/10">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            {company} Interview
            <span className="badge bg-brand-500/20 text-brand-300 border border-brand-500/30 text-sm ml-2">
              Question {sessionData.questionsAsked + 1}
            </span>
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Avg Score: {sessionData.questionsAsked > 0 
              ? (sessionData.totalScore / sessionData.questionsAsked).toFixed(1) 
              : '0.0'} / 10
          </p>
        </div>
        <button onClick={handleEndSession} className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10">
          End Interview
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6 pb-10">
        {/* Question Card */}
        <div className="glass-card p-6 border-l-4 border-l-brand-500">
          <div className="flex items-center gap-3 mb-4">
            <span className="badge bg-white/10 text-gray-300">{currentQuestion?.type}</span>
            <span className={`badge ${
              currentQuestion?.difficulty === 'Hard' ? 'bg-orange-500/20 text-orange-300' :
              currentQuestion?.difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-300' :
              'bg-green-500/20 text-green-300'
            }`}>
              {currentQuestion?.difficulty}
            </span>
          </div>
          <h3 className="text-xl text-white font-medium mb-4 leading-relaxed">
            {currentQuestion?.question}
          </h3>
          {currentQuestion?.company_specific_tip && (
            <div className="bg-brand-900/30 border border-brand-500/20 rounded-lg p-3 text-sm text-brand-200 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span><strong>Tip:</strong> {currentQuestion.company_specific_tip}</span>
            </div>
          )}
        </div>

        {/* Answer Area */}
        {!feedback ? (
          <div className="space-y-4 animate-slide-up">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Your Answer (Treat this as a verbal response or code draft):
            </label>
            <textarea
              className="input-field min-h-[250px] font-mono text-sm"
              placeholder="Type your answer here..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
            />
            <div className="flex justify-end">
              <button
                onClick={handleSubmit}
                disabled={evaluating || !answer.trim()}
                className="btn-primary"
              >
                {evaluating ? (
                  <><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Evaluating...</>
                ) : (
                  <>Submit Answer</>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Feedback Area */
          <div className="animate-slide-up space-y-6">
            <div className="glass-card p-6 border-t-4 border-t-purple-500">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  Evaluation Results
                </h3>
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className={`text-3xl font-black ${
                      feedback.score >= 8 ? 'text-green-400' :
                      feedback.score >= 6 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {feedback.score}/10
                    </div>
                  </div>
                  <div className={`px-4 py-2 rounded-xl border ${
                    feedback.would_proceed 
                      ? 'bg-green-500/10 border-green-500/30 text-green-400'
                      : 'bg-red-500/10 border-red-500/30 text-red-400'
                  } font-semibold flex items-center gap-2`}>
                    {feedback.would_proceed ? <CheckCircle className="w-5 h-5"/> : <XCircle className="w-5 h-5"/>}
                    {feedback.would_proceed ? 'Pass' : 'Needs Work'}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-green-900/10 border border-green-500/20 rounded-xl p-4">
                  <h4 className="text-green-400 font-semibold mb-3 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" /> Strengths
                  </h4>
                  <ul className="space-y-2">
                    {feedback.strengths?.map((s, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-green-500 mt-1">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="bg-red-900/10 border border-red-500/20 rounded-xl p-4">
                  <h4 className="text-red-400 font-semibold mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> Areas for Improvement
                  </h4>
                  <ul className="space-y-2">
                    {feedback.weaknesses?.map((w, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-red-500 mt-1">•</span> {w}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {feedback.missed_points?.length > 0 && (
                <div className="mb-6 bg-white/5 rounded-xl p-4 border border-white/10">
                  <h4 className="text-white font-medium mb-2 text-sm">Key Points Missed:</h4>
                  <ul className="list-disc pl-5 text-sm text-gray-400 space-y-1">
                    {feedback.missed_points.map((m, i) => <li key={i}>{m}</li>)}
                  </ul>
                </div>
              )}

              <div className="bg-brand-900/20 border border-brand-500/20 rounded-xl p-5 mb-6">
                <h4 className="text-brand-300 font-semibold mb-2">Ideal Answer Summary</h4>
                <p className="text-sm text-gray-300 leading-relaxed">{feedback.ideal_answer_summary}</p>
                
                <hr className="my-4 border-brand-500/20" />
                
                <h4 className="text-brand-300 font-semibold mb-2">{company} Specific Feedback</h4>
                <p className="text-sm text-gray-300 leading-relaxed">{feedback.company_specific_feedback}</p>
              </div>

              <div className="flex justify-end gap-4 mt-8 pt-6 border-t border-white/10">
                <button onClick={handleEndSession} className="btn-secondary">
                  End Interview
                </button>
                <button onClick={fetchQuestion} className="btn-primary flex items-center gap-2">
                  Next Question <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
