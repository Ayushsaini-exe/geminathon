import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function Chat() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Namaste! 🌾 I\'m your AgroFix AI assistant. Ask me anything about farming — crop advice, disease info, weather insights, and more.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setLoading(true);
    try {
      const data = await api.post('/api/orchestrator/chat', {
        farmer_id: user?.farmer_id,
        message: msg,
      });
      const response = data.response;
      let botText = '';
      if (typeof response === 'string') {
        botText = response;
      } else if (response?.recommendation) {
        botText = response.recommendation;
      } else if (response?.fertilizer_advice) {
        botText = response.fertilizer_advice;
      } else if (response?.treatment_plan) {
        botText = response.treatment_plan;
      } else {
        botText = JSON.stringify(response, null, 2);
      }
      setMessages(prev => [...prev, {
        role: 'bot',
        text: botText,
        intent: data.intent,
        module: data.module,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: `Sorry, something went wrong: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">AI Chat 💬</div>
          <div className="page-subtitle">Ask anything — powered by Gemini AI + RAG Knowledge Base</div>
        </div>
      </div>
      <div className="page-content">
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.intent && <div className="intent-badge">{m.intent} → {m.module}</div>}
                {m.text}
              </div>
            ))}
            {loading && (
              <div className="chat-bubble bot">
                <span className="spinner" style={{ borderColor: 'var(--gray-300)', borderTopColor: 'var(--green-700)', width: 16, height: 16 }} />
                {' '}Thinking...
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div className="chat-input-row">
            <input
              className="chat-input"
              placeholder="Ask about crops, diseases, fertilizers..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button className="chat-send-btn" onClick={send} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
