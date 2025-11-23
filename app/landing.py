import streamlit as st

# Page config
st.set_page_config(
    page_title="StratifyAI - Company Research Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .hero-section {
        text-align: center;
        padding: 80px 20px 60px;
        color: white;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 20px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        margin-bottom: 40px;
        opacity: 0.95;
        font-weight: 400;
    }
    
    .cta-button {
        background: white;
        color: #667eea;
        padding: 18px 50px;
        font-size: 1.2rem;
        font-weight: 700;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .cta-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .features-section {
        background: white;
        padding: 80px 20px;
        border-radius: 30px 30px 0 0;
        margin-top: 60px;
    }
    
    .section-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 60px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 20px;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 15px;
    }
    
    .feature-description {
        font-size: 1.1rem;
        color: #4a5568;
        line-height: 1.6;
    }
    
    .problem-section {
        background: #f7fafc;
        padding: 60px 20px;
        text-align: center;
    }
    
    .problem-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .problem-text {
        font-size: 1.1rem;
        color: #2d3748;
        font-weight: 600;
    }
    
    .testimonial-section {
        background: white;
        padding: 80px 20px;
    }
    
    .testimonial-card {
        background: #f7fafc;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 4px solid #667eea;
    }
    
    .testimonial-text {
        font-size: 1.1rem;
        color: #2d3748;
        font-style: italic;
        margin-bottom: 15px;
    }
    
    .testimonial-author {
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎯 StratifyAI</div>
    <div class="hero-subtitle">
        AI-Powered Company Research Assistant<br>
        Generate Comprehensive Account Plans in Minutes
    </div>
</div>
""", unsafe_allow_html=True)

# Center the button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🚀 Get Started", key="cta", use_container_width=True):
        st.switch_page("pages/chat.py")

# Problem Section
st.markdown("""
<div class="problem-section">
    <h2 class="section-title">Common Challenges in Company Research</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="problem-card">
        <div class="problem-text">
            😓 Spending hours researching companies manually
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="problem-card">
        <div class="problem-text">
            📊 Struggling to compile comprehensive account plans
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="problem-card">
        <div class="problem-text">
            ⏰ Missing opportunities due to slow research
        </div>
    </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown("""
<div class="features-section">
    <h2 class="section-title">How StratifyAI Helps You Win</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI-Powered Research</div>
        <div class="feature-description">
            Our advanced AI instantly analyzes companies, providing deep insights into their business model, market position, and growth opportunities.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📋</div>
        <div class="feature-title">Comprehensive Account Plans</div>
        <div class="feature-description">
            Generate detailed account plans with key stakeholders, pain points, competitive landscape, and tailored engagement strategies.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Lightning Fast Results</div>
        <div class="feature-description">
            What used to take hours now takes minutes. Get actionable insights and complete account plans in real-time through our AI assistant.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Second row of features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Smart Target Identification</div>
        <div class="feature-description">
            Identify key decision-makers, understand organizational structure, and discover the best entry points for your outreach.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💡</div>
        <div class="feature-title">Strategic Insights</div>
        <div class="feature-description">
            Uncover growth initiatives, recent news, funding rounds, and strategic priorities to tailor your approach perfectly.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💬</div>
        <div class="feature-title">Conversational Interface</div>
        <div class="feature-description">
            Chat naturally with our AI assistant. Ask follow-up questions, request specific details, and refine your research interactively.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Testimonials Section
st.markdown("""
<div class="testimonial-section">
    <h2 class="section-title">What Our Users Say</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="testimonial-card">
        <div class="testimonial-text">
            "StratifyAI has transformed how we approach enterprise accounts. What used to take our team 3-4 hours now takes 10 minutes. The account plans are comprehensive and actionable."
        </div>
        <div class="testimonial-author">- Sarah Chen, Sales Director</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="testimonial-card">
        <div class="testimonial-text">
            "The AI is incredibly intelligent. It understands context, provides relevant insights, and even helps identify opportunities we would have missed. A game-changer for our sales team."
        </div>
        <div class="testimonial-author">- Michael Rodriguez, VP of Sales</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="testimonial-card">
        <div class="testimonial-text">
            "The conversational interface makes research feel natural. I can ask follow-up questions and dive deeper into specific areas. It's like having a research analyst on demand."
        </div>
        <div class="testimonial-author">- Lisa Thompson, Account Executive</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="testimonial-card">
        <div class="testimonial-text">
            "We've seen a 40% increase in meeting conversion rates since using StratifyAI. Our reps are better prepared and can speak directly to the prospect's needs."
        </div>
        <div class="testimonial-author">- James Park, CEO</div>
    </div>
    """, unsafe_allow_html=True)

# Final CTA
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🚀 Start Researching Now", key="cta2", use_container_width=True):
        st.switch_page("pages/chat.py")

st.markdown("<br><br>", unsafe_allow_html=True)
