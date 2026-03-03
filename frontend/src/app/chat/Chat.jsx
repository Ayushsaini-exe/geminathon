import { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { sendChat } from '../../api';
import './Chat.css';

export default function Chat() {
    const [messages, setMessages] = useState([
        { id: 1, text: "Hello! I am the AgroFix AI Assistant. I can help you with crop advisory, identifying diseases, or analyzing your soil. How can I assist you today?", sender: 'bot' }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), text: input, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsTyping(true);

        try {
            const data = await sendChat(userMsg.text);

            let botMessageText = "I'm sorry, I couldn't process that request at this time.";
            if (data.response) {
                if (typeof data.response === 'string') {
                    botMessageText = data.response;
                } else if (data.response.recommendation) {
                    botMessageText = data.response.recommendation;
                } else if (data.response.message) {
                    botMessageText = data.response.message;
                } else if (data.response.error) {
                    // Prettify resource exhausted errors for better UX
                    const errMsg = String(data.response.error);
                    botMessageText = errMsg.includes('429')
                        ? "Currently experiencing high traffic to the AI engine. Please try again in a few moments."
                        : `Error: ${errMsg}`;
                } else {
                    botMessageText = JSON.stringify(data.response);
                }
            } else if (data.message) {
                botMessageText = data.message;
            }

            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: botMessageText,
                sender: 'bot'
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: "Network error: Unable to reach the AI engine right now.",
                sender: 'bot'
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="chat-container glass-panel">
            <div className="chat-header">
                <Bot size={24} color="var(--color-primary)" />
                <div>
                    <h2>AI Advisory Chat</h2>
                    <p>Powered by Gemini and Government Knowledge Bases</p>
                </div>
            </div>

            <div className="chat-messages">
                {messages.map(msg => (
                    <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
                        <div className="message-avatar">
                            {msg.sender === 'bot' ? <Bot size={18} /> : <User size={18} />}
                        </div>
                        <div className={`message-bubble ${msg.sender}`}>
                            <p>{msg.text}</p>
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="message-wrapper bot">
                        <div className="message-avatar"><Bot size={18} /></div>
                        <div className="message-bubble bot typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about your crops..."
                />
                <button type="submit" disabled={!input.trim()}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
}
