import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [clarificationInput, setClarificationInput] = useState('');
  const [showClarificationFor, setShowClarificationFor] = useState(null);
  const [editingSection, setEditingSection] = useState(null);
  const [editInstructions, setEditInstructions] = useState('');
  const [currentEditingReport, setCurrentEditingReport] = useState(null);
  const [currentEditingCompany, setCurrentEditingCompany] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isListeningModal, setIsListeningModal] = useState(false);
  const [speakingMessageIndex, setSpeakingMessageIndex] = useState(null);
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (isListeningModal) {
          setEditInstructions(prev => prev + (prev ? ' ' : '') + transcript);
        } else {
          setInput(prev => prev + (prev ? ' ' : '') + transcript);
        }
        setIsListening(false);
        setIsListeningModal(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setIsListeningModal(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        setIsListeningModal(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, [isListeningModal]);

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

    // Add a progress message
    const progressMessage = {
      role: 'assistant',
      content: '🔍 Starting research...',
      timestamp: new Date().toISOString(),
      isProgress: true,
    };
    setMessages((prev) => [...prev, progressMessage]);

    try {
      // Use EventSource for Server-Sent Events
      const eventSource = new EventSource(`http://localhost:5000/api/research?company_name=${encodeURIComponent(companyName)}`);
      
      // For POST, we need to use fetch with streaming
      const response = await fetch('http://localhost:5000/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_name: companyName }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6));

            if (data.type === 'progress') {
              // Update progress message
              setMessages((prev) => {
                const updated = [...prev];
                const progressIndex = updated.findIndex(m => m.isProgress);
                if (progressIndex !== -1) {
                  updated[progressIndex] = {
                    ...updated[progressIndex],
                    content: data.message,
                  };
                }
                return updated;
              });
            } else if (data.type === 'conflict') {
              // Remove progress message
              setMessages((prev) => prev.filter(m => !m.isProgress));

              // Show conflict question with resolution buttons
              const conflictMessage = {
                role: 'assistant',
                content: `⚠️ **Conflict Detected**\n\n${data.conflict_question}`,
                timestamp: new Date().toISOString(),
                hasConflict: true,
                sessionId: data.session_id,
              };
              setMessages((prev) => [...prev, conflictMessage]);
            } else if (data.type === 'complete') {
              // Remove progress message
              setMessages((prev) => prev.filter(m => !m.isProgress));

              // Show final report
              const assistantMessage = {
                role: 'assistant',
                content: data.report,
                timestamp: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, assistantMessage]);
            } else if (data.type === 'error') {
              // Remove progress message
              setMessages((prev) => prev.filter(m => !m.isProgress));

              const errorMessage = {
                role: 'assistant',
                content: `Error: ${data.message}`,
                timestamp: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, errorMessage]);
            }
          }
        }
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
      // Remove progress message
      setMessages((prev) => prev.filter(m => !m.isProgress));

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
      decisionText = 'Digging deeper to resolve the conflict...';
    } else if (resolution === 'stop') {
      decisionText = 'Continuing with available information...';
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

  const startListening = (forModal = false) => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    if (forModal) {
      setIsListeningModal(true);
    } else {
      setIsListening(true);
    }

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
      setIsListening(false);
      setIsListeningModal(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    setIsListeningModal(false);
  };

  const speakText = (text, messageIndex) => {
    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    if (speakingMessageIndex === messageIndex) {
      // If already speaking this message, stop it
      setSpeakingMessageIndex(null);
      return;
    }

    // Clean the text for speech (remove markdown, emojis, URLs)
    let cleanText = text
      .replace(/#{1,6}\s/g, '') // Remove markdown headers
      .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.+?)\*/g, '$1') // Remove italic
      .replace(/\[(.+?)\]\(.+?\)/g, '$1') // Remove markdown links
      .replace(/https?:\/\/[^\s]+/g, '') // Remove URLs
      .replace(/[⚠️✅🔍📊✓→📝🔄❌]/g, '') // Remove common emojis
      .replace(/\|/g, ' ') // Remove table pipes
      .replace(/\n{2,}/g, '. ') // Replace multiple newlines with period
      .replace(/\n/g, ' ') // Replace single newlines with space
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0; // Normal speed
    utterance.pitch = 1.0; // Normal pitch
    utterance.volume = 1.0; // Full volume

    // Try to use a high-quality voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.lang.startsWith('en') && (voice.name.includes('Google') || voice.name.includes('Microsoft'))
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => {
      setSpeakingMessageIndex(messageIndex);
    };

    utterance.onend = () => {
      setSpeakingMessageIndex(null);
    };

    utterance.onerror = () => {
      setSpeakingMessageIndex(null);
    };

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setSpeakingMessageIndex(null);
  };

  const handleOpenEditModal = (messageIndex, content, companyName) => {
    setCurrentEditingReport({ index: messageIndex, content });
    setCurrentEditingCompany(companyName);
    setEditInstructions('');
  };

  const handleSaveSection = async () => {
    if (!editInstructions.trim() || !currentEditingReport) return;

    setIsLoading(true);

    try {
      const { index, content } = currentEditingReport;
      
      // Add user instruction message
      const instructionMessage = {
        role: 'user',
        content: `Edit report: ${editInstructions}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, instructionMessage]);
      
      // Add progress message
      const progressMessage = {
        role: 'assistant',
        content: `🔄 Updating the report based on your instructions...`,
        timestamp: new Date().toISOString(),
        isProgress: true,
      };
      setMessages((prev) => [...prev, progressMessage]);

      const response = await fetch('http://localhost:5000/api/edit-section', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: currentEditingCompany || 'report',
          edit_instructions: editInstructions,
          full_report: content,
        }),
      });

      const data = await response.json();

      // Remove progress message
      setMessages((prev) => prev.filter(m => !m.isProgress));

      // Add the updated report as a new message
      const updatedReportMessage = {
        role: 'assistant',
        content: data.updated_report,
        timestamp: new Date().toISOString(),
        companyName: currentEditingCompany,
      };
      setMessages((prev) => [...prev, updatedReportMessage]);

      // Close modal
      setCurrentEditingReport(null);
      setCurrentEditingCompany(null);
      setEditInstructions('');
    } catch (error) {
      // Remove progress message
      setMessages((prev) => prev.filter(m => !m.isProgress));
      
      const errorMessage = {
        role: 'assistant',
        content: `❌ Failed to update report: ${error.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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
                      <p className="conflict-prompt">Want to dig deeper into this?</p>
                      <div className="conflict-buttons">
                        <button
                          className="conflict-btn proceed"
                          onClick={() => handleConflictResolution(index, message.sessionId, 'proceed')}
                          disabled={isLoading}
                        >
                          ✓ Yes, Dig Deeper
                        </button>
                        <button
                          className="conflict-btn stop"
                          onClick={() => handleConflictResolution(index, message.sessionId, 'proceed')}
                          disabled={isLoading}
                        >
                          → No, Continue Anyway
                        </button>
                      </div>
                      {/* Read Aloud button for conflict message */}
                      <div className="message-actions" style={{ marginTop: '1rem' }}>
                        <button 
                          className={`action-btn speaker-btn ${speakingMessageIndex === index ? 'speaking' : ''}`}
                          onClick={() => speakText(message.content, index)}
                          title={speakingMessageIndex === index ? 'Stop reading' : 'Read aloud'}
                        >
                          {speakingMessageIndex === index ? (
                            <>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                                <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
                              </svg>
                              Stop Reading
                            </>
                          ) : (
                            <>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M3 9V15H7L12 20V4L7 9H3Z" fill="currentColor"/>
                                <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12Z" fill="currentColor"/>
                                <path d="M14 3.23V5.29C16.89 6.15 19 8.83 19 12C19 15.17 16.89 17.85 14 18.71V20.77C18.01 19.86 21 16.28 21 12C21 7.72 18.01 4.14 14 3.23Z" fill="currentColor"/>
                              </svg>
                              Read Aloud
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                  {message.role === 'assistant' && !message.hasConflict && !message.isProgress && message.content.length > 100 && (
                    <div className="message-actions">
                      <button 
                        className={`action-btn speaker-btn ${speakingMessageIndex === index ? 'speaking' : ''}`}
                        onClick={() => speakText(message.content, index)}
                        title={speakingMessageIndex === index ? 'Stop reading' : 'Read aloud'}
                      >
                        {speakingMessageIndex === index ? (
                          <>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                              <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                              <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
                            </svg>
                            Stop Reading
                          </>
                        ) : (
                          <>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                              <path d="M3 9V15H7L12 20V4L7 9H3Z" fill="currentColor"/>
                              <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12Z" fill="currentColor"/>
                              <path d="M14 3.23V5.29C16.89 6.15 19 8.83 19 12C19 15.17 16.89 17.85 14 18.71V20.77C18.01 19.86 21 16.28 21 12C21 7.72 18.01 4.14 14 3.23Z" fill="currentColor"/>
                            </svg>
                            Read Aloud
                          </>
                        )}
                      </button>
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
                      <button 
                        className="action-btn edit-btn"
                        onClick={() => handleOpenEditModal(index, message.content, message.companyName)}
                      >
                        ✏️ Edit Report
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
              type="button"
              className={`mic-btn ${isListening ? 'listening' : ''}`}
              onClick={() => isListening ? stopListening() : startListening(false)}
              disabled={isLoading}
              title="Voice input"
            >
              {isListening ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="8" fill="currentColor" opacity="0.3"/>
                  <circle cx="12" cy="12" r="4" fill="currentColor"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C10.34 2 9 3.34 9 5V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V5C15 3.34 13.66 2 12 2Z" fill="currentColor"/>
                  <path d="M19 12C19 15.53 16.39 18.44 13 18.93V22H11V18.93C7.61 18.44 5 15.53 5 12H7C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12H19Z" fill="currentColor"/>
                </svg>
              )}
            </button>
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

      {/* Section Edit Modal */}
      {currentEditingReport && (
        <div className="modal-overlay" onClick={() => {
          setCurrentEditingReport(null);
          setCurrentEditingCompany(null);
          setEditInstructions('');
        }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Report</h2>
              <button
                className="modal-close-btn"
                onClick={() => {
                  setCurrentEditingReport(null);
                  setCurrentEditingCompany(null);
                  setEditInstructions('');
                }}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-input-header">
                <p className="edit-instruction-label">
                  Tell me what changes you'd like to make to the report:
                </p>
                <button
                  type="button"
                  className={`modal-mic-btn ${isListeningModal ? 'listening' : ''}`}
                  onClick={() => isListeningModal ? stopListening() : startListening(true)}
                  title="Voice input"
                >
                  {isListeningModal ? (
                    <>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="8" fill="currentColor" opacity="0.3"/>
                        <circle cx="12" cy="12" r="4" fill="currentColor"/>
                      </svg>
                      <span>Listening...</span>
                    </>
                  ) : (
                    <>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2C10.34 2 9 3.34 9 5V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V5C15 3.34 13.66 2 12 2Z" fill="currentColor"/>
                        <path d="M19 12C19 15.53 16.39 18.44 13 18.93V22H11V18.93C7.61 18.44 5 15.53 5 12H7C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12H19Z" fill="currentColor"/>
                      </svg>
                      <span>Use Voice</span>
                    </>
                  )}
                </button>
              </div>
              <textarea
                value={editInstructions}
                onChange={(e) => setEditInstructions(e.target.value)}
                className="section-edit-textarea"
                placeholder="Examples:&#10;- Focus more on the Executive Summary section&#10;- Add more details about their cloud services in Key Insights&#10;- Expand the SWOT analysis with specific examples&#10;- Include information about their recent acquisitions&#10;- Make the Conversation Starters more technical"
                rows="8"
              />
            </div>
            <div className="modal-footer">
              <button
                className="modal-cancel-btn"
                onClick={() => {
                  setCurrentEditingReport(null);
                  setCurrentEditingCompany(null);
                  setEditInstructions('');
                }}
              >
                Cancel
              </button>
              <button
                className="modal-save-btn"
                onClick={handleSaveSection}
                disabled={isLoading || !editInstructions.trim()}
              >
                {isLoading ? 'Updating Report...' : 'Update Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;
