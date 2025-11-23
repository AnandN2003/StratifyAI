import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (companyName) => {
    if (!companyName.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: companyName,
      timestamp: new Date().toISOString(),
      companyName: companyName, // Store company name
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_name: companyName }),
      });

      const data = await response.json();

      if (data.has_conflict) {
        // Show conflict question with resolution buttons
        const conflictMessage = {
          role: 'assistant',
          content: `⚠️ **Conflict Detected**\n\n${data.conflict_question}`,
          timestamp: new Date().toISOString(),
          hasConflict: true,
          sessionId: data.session_id,
        };
        setMessages((prev) => [...prev, conflictMessage]);
      } else {
        // Show final report
        const assistantMessage = {
          role: 'assistant',
          content: data.report,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }

      // Save to chat history
      if (!currentChatId) {
        const newChatId = Date.now().toString();
        setCurrentChatId(newChatId);
        setChatHistory((prev) => [
          {
            id: newChatId,
            company: companyName,
            timestamp: new Date().toLocaleTimeString(),
          },
          ...prev,
        ]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}. Please make sure the backend is running.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConflictResolution = async (messageIndex, sessionId, resolution, clarificationNote = '') => {
    setIsLoading(true);

    // Remove conflict buttons from the message
    setMessages((prev) => {
      const updated = [...prev];
      if (updated[messageIndex]) {
        updated[messageIndex] = {
          ...updated[messageIndex],
          hasConflict: false,
          sessionId: null,
        };
      }
      return updated;
    });

    // Add user's decision as a message
    let decisionText = '';
    if (resolution === 'proceed') {
      decisionText = 'Proceeding with the research anyway...';
    } else if (resolution === 'stop') {
      decisionText = 'Stopping for manual review.';
    } else if (resolution === 'clarify') {
      decisionText = `Adding clarification: "${clarificationNote}"`;
    }

    const userDecisionMessage = {
      role: 'user',
      content: decisionText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userDecisionMessage]);

    try {
      const response = await fetch('http://localhost:5000/api/resolve-conflict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          resolution: resolution,
          clarification_note: clarificationNote,
        }),
      });

      const data = await response.json();

      if (data.status === 'completed') {
        const assistantMessage = {
          role: 'assistant',
          content: data.report,
          timestamp: new Date().toISOString(),
          companyName: messages.find(m => m.role === 'user')?.companyName || 'report', // Get company name from previous messages
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else if (data.status === 'stopped') {
        const assistantMessage = {
          role: 'assistant',
          content: data.message || 'Research stopped for manual review.',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error resolving conflict: ${error.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (content, companyName, format) => {
    if (format === 'pdf') {
      try {
        const response = await fetch('http://localhost:5000/api/download-pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content: content,
            company_name: companyName || 'report',
          }),
        });

        if (!response.ok) throw new Error('PDF generation failed');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${companyName || 'report'}_account_plan.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (error) {
        alert('Failed to generate PDF: ' + error.message);
      }
    } else {
      // MD or TXT download
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `${companyName || 'report'}_account_plan_${timestamp}.${format}`;
      
      const blob = new Blob([content], { type: format === 'md' ? 'text/markdown' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
    setInput('');
  };

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">S</div>
            <span className="logo-text">StratifyAI</span>
          </div>
        </div>

        <button className="new-chat-btn" onClick={handleNewChat}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          New Chat
        </button>

        <div className="chat-history-section">
          <h3 className="history-title">Chat History</h3>
          {chatHistory.length === 0 ? (
            <p className="no-history">No previous chats</p>
          ) : (
            <div className="chat-history-list">
              {chatHistory.map((chat) => (
                <div key={chat.id} className="chat-history-item">
                  <div className="history-company">{chat.company}</div>
                  <div className="history-time">{chat.timestamp}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="chat-main">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <h1 className="welcome-title">How can I help you today?</h1>
            <p className="welcome-subtitle">
              Ask me to research any company for account planning
            </p>
            <div className="example-buttons">
              <button
                className="example-btn"
                onClick={() => handleSubmit('Tesla')}
              >
                Research Tesla
              </button>
              <button
                className="example-btn"
                onClick={() => handleSubmit('Microsoft')}
              >
                Research Microsoft
              </button>
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                {message.role === 'assistant' && (
                  <div className="message-avatar">
                    <div className="avatar-icon">S</div>
                  </div>
                )}
                <div className="message-content">
                  <div className="message-text">
                    {message.content.split('\n').map((line, i) => (
                      <React.Fragment key={i}>
                        {line}
                        {i < message.content.split('\n').length - 1 && <br />}
                      </React.Fragment>
                    ))}
                  </div>
                  {message.role === 'assistant' && message.hasConflict && message.sessionId && (
                    <div className="conflict-actions">
                      <p className="conflict-prompt">How would you like to proceed?</p>
                      <div className="conflict-buttons">
                        <button
                          className="conflict-btn proceed"
                          onClick={() => handleConflictResolution(index, message.sessionId, 'proceed')}
                          disabled={isLoading}
                        >
                          ✓ Proceed Anyway
                        </button>
                        <button
                          className="conflict-btn stop"
                          onClick={() => handleConflictResolution(index, message.sessionId, 'stop')}
                          disabled={isLoading}
                        >
                          ✋ Stop for Review
                        </button>
                        <button
                          className="conflict-btn clarify"
                          onClick={() => {
                            const note = prompt('Enter your clarification note:');
                            if (note) {
                              handleConflictResolution(index, message.sessionId, 'clarify', note);
                            }
                          }}
                          disabled={isLoading}
                        >
                          📝 Add Clarification
                        </button>
                      </div>
                    </div>
                  )}
                  {message.role === 'assistant' && !message.hasConflict && message.content.length > 100 && (
                    <div className="message-actions">
                      <button 
                        className="action-btn"
                        onClick={() => handleDownload(message.content, message.companyName, 'pdf')}
                      >
                        Download PDF
                      </button>
                      <button 
                        className="action-btn"
                        onClick={() => handleDownload(message.content, message.companyName, 'md')}
                      >
                        Download MD
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant-message">
                <div className="message-avatar">
                  <div className="avatar-icon">S</div>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input Area */}
        <div className="input-container">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(input);
            }}
            className="input-form"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a company name to research..."
              className="chat-input"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-btn"
              disabled={!input.trim() || isLoading}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M22 2L11 13M22 2L15 22L11 13M22 2L2 8L11 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default Chat;
