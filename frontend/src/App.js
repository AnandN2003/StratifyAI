import React from 'react';
import './App.css';

function App() {
  const handleGetStarted = () => {
    // Redirect to Streamlit app running on port 8501
    window.location.href = 'http://localhost:8501';
  };

  return (
    <div className="App">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">🎯 StratifyAI</h1>
          <p className="hero-subtitle">
            AI-Powered Company Research Assistant<br />
            Generate Comprehensive Account Plans in Minutes
          </p>
          <button className="cta-button" onClick={handleGetStarted}>
            🚀 Get Started
          </button>
        </div>
      </section>

      {/* Problems Section */}
      <section className="problems">
        <h2 className="section-title">Common Challenges in Company Research</h2>
        <div className="problems-grid">
          <div className="problem-card">
            <div className="problem-text">
              😓 Spending hours researching companies manually
            </div>
          </div>
          <div className="problem-card">
            <div className="problem-text">
              📊 Struggling to compile comprehensive account plans
            </div>
          </div>
          <div className="problem-card">
            <div className="problem-text">
              ⏰ Missing opportunities due to slow research
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">How StratifyAI Helps You Win</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3 className="feature-title">AI-Powered Research</h3>
            <p className="feature-description">
              Our advanced AI instantly analyzes companies, providing deep insights into their business model, market position, and growth opportunities.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📋</div>
            <h3 className="feature-title">Comprehensive Account Plans</h3>
            <p className="feature-description">
              Generate detailed account plans with key stakeholders, pain points, competitive landscape, and tailored engagement strategies.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Lightning Fast Results</h3>
            <p className="feature-description">
              What used to take hours now takes minutes. Get actionable insights and complete account plans in real-time through our AI assistant.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3 className="feature-title">Smart Target Identification</h3>
            <p className="feature-description">
              Identify key decision-makers, understand organizational structure, and discover the best entry points for your outreach.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">💡</div>
            <h3 className="feature-title">Strategic Insights</h3>
            <p className="feature-description">
              Uncover growth initiatives, recent news, funding rounds, and strategic priorities to tailor your approach perfectly.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3 className="feature-title">Conversational Interface</h3>
            <p className="feature-description">
              Chat naturally with our AI assistant. Ask follow-up questions, request specific details, and refine your research interactively.
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <h2 className="section-title">What Our Users Say</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <p className="testimonial-text">
              "StratifyAI has transformed how we approach enterprise accounts. What used to take our team 3-4 hours now takes 10 minutes. The account plans are comprehensive and actionable."
            </p>
            <p className="testimonial-author">- Sarah Chen, Sales Director</p>
          </div>
          
          <div className="testimonial-card">
            <p className="testimonial-text">
              "The AI is incredibly intelligent. It understands context, provides relevant insights, and even helps identify opportunities we would have missed. A game-changer for our sales team."
            </p>
            <p className="testimonial-author">- Michael Rodriguez, VP of Sales</p>
          </div>
          
          <div className="testimonial-card">
            <p className="testimonial-text">
              "The conversational interface makes research feel natural. I can ask follow-up questions and dive deeper into specific areas. It's like having a research analyst on demand."
            </p>
            <p className="testimonial-author">- Lisa Thompson, Account Executive</p>
          </div>
          
          <div className="testimonial-card">
            <p className="testimonial-text">
              "We've seen a 40% increase in meeting conversion rates since using StratifyAI. Our reps are better prepared and can speak directly to the prospect's needs."
            </p>
            <p className="testimonial-author">- James Park, CEO</p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta">
        <button className="cta-button large" onClick={handleGetStarted}>
          🚀 Start Researching Now
        </button>
      </section>
    </div>
  );
}

export default App;
