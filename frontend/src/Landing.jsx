import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

function Landing() {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 50;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrolled]);

  const handleGetStarted = () => {
    navigate('/chat');
  };

  return (
    <div className="App">
      {/* Header/Navigation */}
      <header className={`header ${scrolled ? 'scrolled' : ''}`}>
        <div className="logo">
          <div className="logo-icon">S</div>
          <span className="logo-text">STRATIFYAI</span>
        </div>
        <nav className="nav">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#testimonials">Testimonials</a>
        </nav>
        <div className="header-buttons">
          <button className="btn-signin">Sign In</button>
          <button className="btn-demo" onClick={handleGetStarted}>Book a Demo</button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            AI Powered Company Research <br/>
            Assistant that Actually <span className="highlight">Works</span>
          </h1>
          <p className="hero-subtitle">
            Use AI to find prospects that need you, automatically craft<br/>
            personalized account plans for each, and scale effortlessly
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={handleGetStarted}>
              Get Started →
            </button>
            <button className="btn-secondary" onClick={handleGetStarted}>
              📅 Book a Demo
            </button>
          </div>
        </div>
      </section>

      {/* Problems Section */}
      <section className="problems" id="features">
        <h2 className="section-title">Common Challenges in Company Research</h2>
        <div className="problems-grid">
          <div className="problem-card">
            <div className="problem-text">
              Spending hours researching companies manually
            </div>
          </div>
          <div className="problem-card">
            <div className="problem-text">
              Struggling to compile comprehensive account plans
            </div>
          </div>
          <div className="problem-card">
            <div className="problem-text">
              Missing opportunities due to slow research
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">How StratifyAI Helps You Win</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 3H15M9 21H15M3 9V15M21 9V15M4.22 4.22L6.34 6.34M17.66 17.66L19.78 19.78M4.22 19.78L6.34 17.66M17.66 6.34L19.78 4.22M12 8V16M8 12H16" stroke="#ff4444" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h3 className="feature-title">AI-Powered Research</h3>
            <p className="feature-description">
              Advanced AI instantly analyzes companies, providing deep insights into their business model, market position, and growth opportunities.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M9 12H15M9 16H15" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Comprehensive Account Plans</h3>
            <p className="feature-description">
              Generate detailed account plans with key stakeholders, pain points, competitive landscape, and tailored engagement strategies.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 10V3L4 14H11L11 21L20 10L13 10Z" stroke="#ff4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Lightning Fast Results</h3>
            <p className="feature-description">
              What used to take hours now takes minutes. Get actionable insights and complete account plans in real-time through our AI assistant.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="9" stroke="#8b5cf6" strokeWidth="2"/>
                <path d="M12 6V12L16 14" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Smart Target Identification</h3>
            <p className="feature-description">
              Identify key decision-makers, understand organizational structure, and discover the best entry points for your outreach.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.663 17H14.337C14.6765 17 14.9454 16.7312 14.9454 16.3917V12.6083C14.9454 12.2688 14.6765 12 14.337 12H9.663C9.32346 12 9.05457 12.2688 9.05457 12.6083V16.3917C9.05457 16.7312 9.32346 17 9.663 17Z" stroke="#ff4444" strokeWidth="2"/>
                <path d="M12 9V12M12 9C10.3431 9 9 7.65685 9 6C9 4.34315 10.3431 3 12 3C13.6569 3 15 4.34315 15 6C15 7.65685 13.6569 9 12 9Z" stroke="#ff4444" strokeWidth="2" strokeLinecap="round"/>
                <path d="M19 17V21M5 17V21M21 19H17M7 19H3" stroke="#ff4444" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Strategic Insights</h3>
            <p className="feature-description">
              Uncover growth initiatives, recent news, funding rounds, and strategic priorities to tailor your approach perfectly.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 12H8.01M12 12H12.01M16 12H16.01M21 12C21 16.4183 16.9706 20 12 20C10.4607 20 9.01172 19.6565 7.74467 19.0511L3 20L4.39499 16.28C3.51156 15.0423 3 13.5743 3 12C3 7.58172 7.02944 4 12 4C16.9706 4 21 7.58172 21 12Z" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Conversational Interface</h3>
            <p className="feature-description">
              Chat naturally with our AI assistant. Ask follow-up questions, request specific details, and refine your research interactively.
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials" id="testimonials">
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
          Start Researching Now
        </button>
      </section>
    </div>
  );
}

export default Landing;
