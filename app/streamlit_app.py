import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the Python path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import AgentState, create_research_graph
import json
from typing import Optional
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import markdown2
import re
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="StratifyAI - AI-Powered Cold Outreach",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - ELEGANT BLACK/BLUE THEME WITH ANIMATED BACKGROUND
# ============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* Animated Background */
@keyframes moveBackground {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Main App Container */
.stApp {
    background: linear-gradient(
        135deg,
        #0a0e27 0%,
        #141b3d 25%,
        #1a2451 50%,
        #141b3d 75%,
        #0a0e27 100%
    );
    background-size: 400% 400%;
    animation: moveBackground 20s ease infinite;
    font-family: 'Inter', sans-serif;
}

/* Radial Gradient Overlays for Depth */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at 30% 50%,
        rgba(76, 114, 255, 0.1) 0%,
        transparent 50%
    ),
    radial-gradient(
        circle at 70% 50%,
        rgba(138, 43, 226, 0.08) 0%,
        transparent 50%
    );
    pointer-events: none;
    z-index: 0;
}

/* Hero Title Styling */
.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(135deg, #ffffff 0%, #4C72FF 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.25rem;
    text-align: center;
    color: #94a3b8;
    font-weight: 300;
    margin-bottom: 2rem;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #4C72FF 0%, #6366f1 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 114, 255, 0.3);
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(76, 114, 255, 0.5);
    background: linear-gradient(135deg, #5d82ff 0%, #7477f2 100%);
}

/* Input Fields */
.stTextInput > div > div > input {
    background-color: rgba(15, 23, 42, 0.6);
    border: 2px solid rgba(76, 114, 255, 0.3);
    border-radius: 10px;
    color: #e2e8f0;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #4C72FF;
    box-shadow: 0 0 0 3px rgba(76, 114, 255, 0.2);
}

/* Status Box */
.status-box {
    background: rgba(15, 23, 42, 0.7);
    border: 2px solid rgba(76, 114, 255, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

/* Conflict Alert Box */
.conflict-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border: 2px solid rgba(239, 68, 68, 0.5);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

/* Report Box */
.report-box {
    background: rgba(15, 23, 42, 0.8);
    border: 2px solid rgba(76, 114, 255, 0.4);
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    color: #e2e8f0;
}

/* Expander Styling */
.streamlit-expanderHeader {
    background-color: rgba(15, 23, 42, 0.6);
    border-radius: 10px;
    color: #e2e8f0;
    font-weight: 600;
}

/* Markdown Text Color */
.stMarkdown, p, h1, h2, h3, h4, h5, h6, li {
    color: #e2e8f0 !important;
}

/* Table Styling */
table {
    color: #e2e8f0 !important;
    background-color: rgba(15, 23, 42, 0.5);
}

thead th {
    background-color: rgba(76, 114, 255, 0.2);
    color: #ffffff !important;
}

tbody tr:nth-child(even) {
    background-color: rgba(15, 23, 42, 0.3);
}

/* Spinner */
.stSpinner > div {
    border-top-color: #4C72FF !important;
}

/* Success/Error Messages */
.stSuccess {
    background-color: rgba(34, 197, 94, 0.1);
    border-left: 4px solid #22c55e;
    color: #86efac !important;
}

.stError {
    background-color: rgba(239, 68, 68, 0.1);
    border-left: 4px solid #ef4444;
    color: #fca5a5 !important;
}

.stInfo {
    background-color: rgba(76, 114, 255, 0.1);
    border-left: 4px solid #4C72FF;
    color: #93c5fd !important;
}

/* Columns */
.element-container {
    color: #e2e8f0;
}

/* Code Blocks */
code {
    background-color: rgba(15, 23, 42, 0.8);
    color: #93c5fd;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
}

pre {
    background-color: rgba(15, 23, 42, 0.9);
    border-radius: 8px;
    padding: 1rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

def generate_pdf_from_markdown(markdown_text: str, company_name: str) -> BytesIO:
    """
    Generate a PDF from markdown text.
    
    Args:
        markdown_text: The markdown content to convert
        company_name: Name of the company for the filename
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4C72FF'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=16
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Story (content container)
    story = []
    
    # Add header
    story.append(Paragraph(f"Account Plan Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    def clean_text_for_pdf(text):
        """Clean and properly format text for PDF, handling bold markers."""
        # Replace **text** with proper <b>text</b> tags
        # Handle cases where ** might be unmatched
        parts = text.split('**')
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are between ** markers (bold)
                result.append(f'<b>{part}</b>')
            else:
                result.append(part)
        
        final_text = ''.join(result)
        
        # Escape any remaining problematic characters
        final_text = final_text.replace('&', '&amp;')
        final_text = final_text.replace('<', '&lt;').replace('>', '&gt;')
        # Re-enable our bold tags
        final_text = final_text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        
        return final_text
    
    # Parse markdown and convert to PDF elements
    lines = markdown_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, heading1_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading2_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, heading2_style))
        
        # Handle bullet points
        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:].strip()
            clean_text = clean_text_for_pdf(text)
            story.append(Paragraph(f"• {clean_text}", bullet_style))
        
        # Handle numbered lists
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line).strip()
            clean_text = clean_text_for_pdf(text)
            story.append(Paragraph(clean_text, bullet_style))
        
        # Handle tables (simple markdown tables)
        elif '|' in line and not line.startswith('|:'):
            # Collect table rows
            table_data = []
            while i < len(lines) and '|' in lines[i]:
                row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                if row and not lines[i].startswith('|:'):  # Skip separator rows
                    table_data.append(row)
                i += 1
            
            if table_data:
                # Create table
                table = Table(table_data, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4C72FF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
            continue  # Skip the increment since we already processed multiple lines
        
        # Regular paragraph
        else:
            clean_text = clean_text_for_pdf(line)
            story.append(Paragraph(clean_text, body_style))
        
        i += 1
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables."""
    if 'agent_state' not in st.session_state:
        st.session_state.agent_state = None
    if 'is_conflict' not in st.session_state:
        st.session_state.is_conflict = False
    if 'final_report' not in st.session_state:
        st.session_state.final_report = None
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'execution_log' not in st.session_state:
        st.session_state.execution_log = []
    if 'research_count' not in st.session_state:
        st.session_state.research_count = 0
    if 'conflict_question' not in st.session_state:
        st.session_state.conflict_question = ""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'config' not in st.session_state:
        st.session_state.config = None

initialize_session_state()


# ============================================================================
# BACKEND INTEGRATION FUNCTIONS
# ============================================================================

def run_agent_cycle(company_name: str) -> None:
    """
    Execute the LangGraph agent with the given company name.
    
    This function:
    1. Initializes the AgentState with the company name
    2. Runs the graph until completion or human review interruption
    3. Updates session state with results
    
    Args:
        company_name: Name of the company to research
    """
    try:
        st.session_state.processing = True
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "company_name": company_name,
            "research_data": [],
            "conflicting_info": False,
            "clarification_question": "",
            "conflicting_data": "",
            "final_report": "",
            "human_resolution": ""
        }
        
        # Create graph
        graph = create_research_graph()
        
        # Create a thread config for checkpointing
        config = {"configurable": {"thread_id": "stratify_session_1"}}
        
        # Run the agent - this will execute until it hits the interrupt or completes
        result_state = graph.invoke(initial_state, config)
        
        # Store the complete agent state
        st.session_state.agent_state = result_state
        st.session_state.execution_log = result_state.get("messages", [])
        st.session_state.research_count = len(result_state.get("research_data", []))
        st.session_state.config = config  # Save config for resuming
        
        # Debug logging
        st.session_state.execution_log.append(f"\n🔍 DEBUG: Conflicting info = {result_state.get('conflicting_info', False)}")
        st.session_state.execution_log.append(f"🔍 DEBUG: Final report length = {len(result_state.get('final_report', ''))}")
        st.session_state.execution_log.append(f"🔍 DEBUG: Clarification question = {result_state.get('clarification_question', 'None')}")
        
        # Check if there's a conflict requiring human review
        if result_state.get("conflicting_info", False):
            st.session_state.is_conflict = True
            st.session_state.conflict_question = result_state.get("clarification_question", "A conflict was detected in the research data.")
            st.session_state.final_report = None
            st.session_state.report_generated = False
            st.session_state.execution_log.append("✋ PAUSED: Waiting for human review")
        else:
            # No conflict - report should be ready
            st.session_state.is_conflict = False
            final_report = result_state.get("final_report", "")
            
            if final_report:
                st.session_state.final_report = final_report
                st.session_state.report_generated = True
                st.session_state.execution_log.append("✅ SUCCESS: Report generated")
            else:
                st.session_state.execution_log.append("⚠️ WARNING: No final report in state")
                st.session_state.report_generated = False
            
    except Exception as e:
        st.error(f"❌ Error during agent execution: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        st.code(error_trace, language="python")
        st.session_state.execution_log.append(f"ERROR: {str(e)}\n{error_trace}")
    finally:
        st.session_state.processing = False


def resolve_conflict(resolution: str) -> None:
    """
    Resume the agent after human conflict resolution.
    
    This function:
    1. Retrieves the suspended agent state
    2. Applies the human resolution
    3. Continues the graph execution (proceeds to Writer)
    
    Args:
        resolution: Human decision ('proceed', 'stop', or custom clarification)
    """
    try:
        st.session_state.processing = True
        
        if st.session_state.agent_state is None:
            st.error("No agent state found. Please start a new research cycle.")
            return
        
        # Get the current state from the stored state
        current_state = st.session_state.agent_state.copy()
        messages = current_state.get("messages", []).copy()
        research_data = current_state.get("research_data", []).copy()
        
        # Apply human resolution
        if resolution == "proceed":
            messages.append("👤 HUMAN DECISION: Proceed despite conflict")
            current_state["human_resolution"] = "proceed"
            current_state["conflicting_info"] = False
            
        elif resolution == "stop":
            messages.append("👤 HUMAN DECISION: Stop for manual review")
            current_state["human_resolution"] = "stop"
            current_state["final_report"] = f"# Account Plan: {current_state['company_name']}\n\n**PAUSED FOR MANUAL REVIEW**\n\nConflict: {st.session_state.conflict_question}"
            current_state["messages"] = messages
            st.session_state.final_report = current_state["final_report"]
            st.session_state.report_generated = True
            st.session_state.is_conflict = False
            st.session_state.agent_state = current_state
            return
            
        else:  # Custom clarification
            messages.append(f"👤 HUMAN CLARIFICATION: {resolution}")
            research_data.append({
                "query": "Human Clarification",
                "title": "Manual Review Note",
                "url": "human-input",
                "content": resolution,
                "score": 1.0
            })
            current_state["human_resolution"] = "clarification"
            current_state["conflicting_info"] = False
        
        # Update state with resolution
        current_state["messages"] = messages
        current_state["research_data"] = research_data
        
        # Now manually call the writer node since we're past the interrupt
        from src.graph import writer_node
        
        st.session_state.execution_log.append("🔄 Resuming: Calling writer node...")
        
        # Call writer directly with the updated state
        final_state = writer_node(current_state)
        
        # Update session state
        st.session_state.agent_state = final_state
        st.session_state.execution_log = final_state.get("messages", [])
        st.session_state.execution_log.append(f"🔍 DEBUG: Writer returned report length = {len(final_state.get('final_report', ''))}")
        
        final_report = final_state.get("final_report", "")
        
        if final_report:
            st.session_state.final_report = final_report
            st.session_state.report_generated = True
            st.session_state.is_conflict = False
            st.session_state.execution_log.append("✅ SUCCESS: Report generated after human resolution")
        else:
            st.session_state.execution_log.append("⚠️ WARNING: Writer node did not produce a report")
        
    except Exception as e:
        st.error(f"❌ Error during conflict resolution: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        st.code(error_trace, language="python")
        st.session_state.execution_log.append(f"ERROR during resolution: {str(e)}\n{error_trace}")
    finally:
        st.session_state.processing = False


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_hero_section():
    """Render the hero section with company input."""
    st.markdown(
        '<h1 class="hero-title">AI Powered Cold Outreach that<br>Actually Reaches the Inbox</h1>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<p class="hero-subtitle">Use AI to find prospects that need you, automatically craft personalized cold emails for each, and scale effortlessly</p>',
        unsafe_allow_html=True
    )
    
    # Company Input Form
    with st.form("company_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            company_input = st.text_input(
                "Company Name",
                placeholder="Enter company name (e.g., Tesla, Microsoft)",
                key="company_input",
                label_visibility="collapsed"
            )
            
            submit_button = st.form_submit_button("🚀 Start Research", use_container_width=True)
            
            if submit_button and company_input:
                try:
                    with st.spinner("🔍 Researching company... This may take a minute..."):
                        run_agent_cycle(company_input)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error starting research: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")


def render_execution_status():
    """Render the execution status and logs."""
    if st.session_state.execution_log or st.session_state.processing:
        st.markdown("---")
        st.markdown("## 📊 Execution Status")
        
        with st.expander("📋 View Execution Log", expanded=True):
            if st.session_state.processing:
                st.info("⏳ Agent is processing...")
            
            for log_entry in st.session_state.execution_log:
                st.text(log_entry)
            
            # Debug info
            if st.session_state.agent_state:
                st.markdown("### 🔍 Debug Info")
                st.write(f"**Conflicting Info:** {st.session_state.agent_state.get('conflicting_info', 'N/A')}")
                st.write(f"**Final Report Present:** {bool(st.session_state.agent_state.get('final_report'))}")
                st.write(f"**Report Length:** {len(st.session_state.agent_state.get('final_report', ''))}")
        
        # Show research statistics
        if st.session_state.research_count > 0:
            st.info(f"✅ Collected {st.session_state.research_count} research findings")


def render_conflict_resolution():
    """Render the conflict resolution interface."""
    if st.session_state.is_conflict and not st.session_state.processing:
        st.markdown("---")
        st.markdown("## ⚠️ Conflict Detected - Human Review Required")
        
        st.markdown(
            f'<div class="conflict-box"><h3>🤔 Clarification Needed</h3><p>{st.session_state.conflict_question}</p></div>',
            unsafe_allow_html=True
        )
        
        st.markdown("### How would you like to proceed?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Proceed Anyway", use_container_width=True, help="Ignore the conflict and generate the report"):
                try:
                    with st.spinner("Generating report..."):
                        resolve_conflict("proceed")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error proceeding: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
        
        with col2:
            if st.button("🛑 Stop & Review", use_container_width=True, help="Stop here for manual review"):
                try:
                    with st.spinner("Stopping for review..."):
                        resolve_conflict("stop")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error stopping: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
        
        with col3:
            st.markdown("")  # Placeholder for alignment
        
        # Custom clarification option
        st.markdown("### Or provide clarification:")
        clarification_input = st.text_area(
            "Clarification",
            placeholder="Enter your clarification or additional context...",
            key="clarification_input",
            label_visibility="collapsed",
            height=100
        )
        
        if st.button("📝 Submit Clarification", use_container_width=False):
            if clarification_input:
                try:
                    with st.spinner("Processing clarification..."):
                        resolve_conflict(clarification_input)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error submitting clarification: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
            else:
                st.warning("Please enter a clarification before submitting.")


def render_final_report():
    """Render the final account plan report."""
    if st.session_state.report_generated and st.session_state.final_report:
        st.markdown("---")
        st.markdown("## 📄 Final Account Plan")
        
        # Success message
        st.success("✅ Account plan generated successfully!")
        
        # Display report
        st.markdown(
            f'<div class="report-box">{st.session_state.final_report}</div>',
            unsafe_allow_html=True
        )
        
        # Download buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Download Markdown
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.final_report,
                file_name=f"account_plan_{st.session_state.agent_state['company_name'].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            # Generate and Download PDF
            try:
                pdf_buffer = generate_pdf_from_markdown(
                    st.session_state.final_report,
                    st.session_state.agent_state['company_name']
                )
                
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_buffer,
                    file_name=f"account_plan_{st.session_state.agent_state['company_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.info("💡 PDF report is ready for download!")
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")
        
        # Reset button
        if st.button("🔄 Research Another Company"):
            try:
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error resetting: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point."""
    
    # Render hero section
    render_hero_section()
    
    # Render execution status
    render_execution_status()
    
    # Render conflict resolution if needed
    render_conflict_resolution()
    
    # Render final report if available
    render_final_report()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #64748b; font-size: 0.9rem;">Powered by LangGraph, Gemini AI, and Tavily Research</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
