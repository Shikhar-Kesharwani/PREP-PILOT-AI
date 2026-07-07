import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// Chat
export const askQuestion = (query, sessionId, userId) =>
  api.post('/api/chat/ask', { query, session_id: sessionId, user_id: userId });

// Interview
export const getCompanies = () =>
  api.get('/api/interview/companies');

export const getCompanyQuestion = (company, previousQuestions = [], topic = null) =>
  api.post('/api/interview/company/question', {
    company, previous_questions: previousQuestions, topic,
  });

export const evaluateAnswer = (company, question, answer, interviewType, expectedPoints, sessionId) =>
  api.post('/api/interview/company/evaluate', {
    company, question, answer,
    interview_type: interviewType,
    expected_points: expectedPoints,
    session_id: sessionId,
  });

export const saveSession = (data) =>
  api.post('/api/interview/session', data);

// Progress
export const getDashboard = (userId) =>
  api.get(`/api/progress/dashboard/${userId}`);

export const getChatStats = (userId) =>
  api.get(`/api/progress/chat-stats/${userId}`);

export default api;
