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
import uuid

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="StratifyAI - AI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - CHAT INTERFACE THEME (ChatGPT-style)
# ============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Main App Background */
.stApp {
    background: #0d1117;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #1c1c1c;
    border-right: 1px solid #2d2d2d;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #e8e8e8;
}

/* Sidebar Chat History */
.chat-history-item {
    background: #2d2d2d;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.chat-history-item:hover {
    background: #3d3d3d;
    border-color: #4d4d4d;
}

.chat-history-item.active {
    background: #3d3d3d;
    border-color: #10a37f;
}

/* Main Chat Container */
.main .block-container {
    padding: 2rem 1rem;
    max-width: 900px;
    margin: 0 auto;
}

/* Chat Message Bubbles */
.chat-message {
    display: flex;
    margin-bottom: 1.5rem;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
    justify-content: flex-end;
}

.chat-message.assistant {
    justify-content: flex-start;
}

.message-content {
    max-width: 75%;
    padding: 14px 18px;
    border-radius: 18px;
    line-height: 1.6;
    word-wrap: break-word;
}

.message-content.user {
    background: #10a37f;
    color: white;
    border-bottom-right-radius: 4px;
}

.message-content.assistant {
    background: #2d2d2d;
    color: #e8e8e8;
    border-bottom-left-radius: 4px;
}

.message-content.system {
    background: #3d3d3d;
    color: #a8a8a8;
    font-style: italic;
    max-width: 100%;
    text-align: center;
    border-radius: 8px;
}

/* Typing Indicator */
.typing-indicator {
    display: flex;
    align-items: center;
    padding: 14px 18px;
    background: #2d2d2d;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    max-width: 75%;
}

.typing-dot {
    width: 8px;
    height: 8px;
    margin: 0 3px;
    background: #10a37f;
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
    30% { transform: translateY(-10px); opacity: 1; }
}

/* Input Area */
.stTextInput > div > div > input {
    background: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 12px;
    color: #e8e8e8;
    padding: 14px 18px;
    font-size: 1rem;
}

.stTextInput > div > div > input:focus {
    border-color: #10a37f;
    box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
}

/* Buttons */
.stButton > button {
    background: #10a37f;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #0d8c6a;
    transform: translateY(-1px);
}

/* Conflict Resolution Options */
.conflict-option {
    background: #2d2d2d;
    border: 2px solid #3d3d3d;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    cursor: pointer;
    transition: all 0.2s ease;
}

.conflict-option:hover {
    border-color: #10a37f;
    background: #3d3d3d;
}

/* Markdown in Chat */
.message-content h1, .message-content h2, .message-content h3 {
    color: #e8e8e8;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}

.message-content p {
    margin: 0.5em 0;
    color: #e8e8e8;
}

.message-content code {
    background: #1c1c1c;
    padding: 2px 6px;
    border-radius: 4px;
    color: #10a37f;
}

.message-content pre {
    background: #1c1c1c;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
}

/* Report Download Section */
.download-section {
    background: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}

/* Welcome Screen */
.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
}

.welcome-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #e8e8e8;
    margin-bottom: 1rem;
}

.welcome-subtitle {
    font-size: 1.1rem;
    color: #a8a8a8;
    margin-bottom: 2rem;
    max-width: 600px;
}

.example-prompts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 12px;
    margin-top: 2rem;
    width: 100%;
    max-width: 800px;
}

.example-prompt {
    background: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
}

.example-prompt:hover {
    background: #3d3d3d;
    border-color: #10a37f;
    transform: translateY(-2px);
}

.example-prompt-title {
    font-weight: 600;
    color: #e8e8e8;
    margin-bottom: 6px;
}

.example-prompt-desc {
    font-size: 0.9rem;
    color: #a8a8a8;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1c1c1c;
}

::-webkit-scrollbar-thumb {
    background: #3d3d3d;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4d4d4d;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.5rem;
    }
    
    .message-content {
        max-width: 90%;
    }
    
    .welcome-title {
        font-size: 2rem;
    }
    
    .example-prompts {
        grid-template-columns: 1fr;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

def generate_pdf_from_markdown(markdown_text: str, company_name: str) -> BytesIO:
    """
    Generate a professional PDF from markdown text with dark theme styling.
    
    Args:
        markdown_text: The markdown content to convert
        company_name: Name of the company for the filename
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        topMargin=0.75*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles matching the dark theme
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a2451'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderPadding=10,
        leftIndent=0
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
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=10,
        alignment=TA_LEFT,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        leftIndent=30,
        bulletIndent=15,
        leading=14
    )
    
    source_link_style = ParagraphStyle(
        'SourceLink',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#4C72FF'),
        spaceAfter=8,
        leftIndent=20,
        leading=12
    )
    
    # Story (content container)
    story = []
    
    # Add header with company branding
    story.append(Paragraph("Account Plan Report", title_style))
    story.append(Paragraph(f"{company_name} | Generated on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    def clean_text_for_pdf(text):
        """Clean and properly format text for PDF, handling bold markers."""
        # Replace **text** with proper <b>text</b> tags
        parts = text.split('**')
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are between ** markers (bold)
                result.append(f'<b>{part}</b>')
            else:
                result.append(part)
        
        final_text = ''.join(result)
        
        # Escape problematic characters but preserve our HTML tags
        final_text = final_text.replace('&', '&amp;')
        final_text = final_text.replace('<', '&lt;').replace('>', '&gt;')
        final_text = final_text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        final_text = final_text.replace('&lt;br&gt;', '<br/>')
        final_text = final_text.replace('&lt;br/&gt;', '<br/>')
        
        return final_text
    
    # Parse markdown and convert to PDF elements
    lines = markdown_text.split('\n')
    
    i = 0
    in_table = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            if not in_table:
                story.append(Spacer(1, 0.1*inch))
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# ') and not line.startswith('## '):
            text = line[2:].strip()
            # Add separator line before major sections
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph(text, heading1_style))
            
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading2_style))
            
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, heading2_style))
        
        # Handle horizontal rules
        elif line.startswith('---'):
            story.append(Spacer(1, 0.2*inch))
            
        # Handle bullet points
        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:].strip()
            clean_text = clean_text_for_pdf(text)
            story.append(Paragraph(f"• {clean_text}", bullet_style))
        
        # Handle numbered lists (including source links)
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line).strip()
            
            # Check if it's a markdown link [text](url)
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', text)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                formatted_text = f'<b>{link_text}</b><br/><font size="8" color="#666666">{link_url}</font>'
                story.append(Paragraph(formatted_text, source_link_style))
            else:
                clean_text = clean_text_for_pdf(text)
                story.append(Paragraph(clean_text, bullet_style))
        
        # Handle tables
        elif '|' in line and not line.startswith('|:'):
            in_table = True
            table_data = []
            
            while i < len(lines) and '|' in lines[i]:
                row_text = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                if row_text and not lines[i].startswith('|:'):
                    # Wrap each cell in a Paragraph for proper text wrapping
                    row_paragraphs = []
                    for idx, cell in enumerate(row_text):
                        if idx == 0:  # First column (Category) - use bold
                            row_paragraphs.append(Paragraph(f"<b>{cell}</b>", body_style))
                        else:  # Second column (Summary) - regular text with wrapping
                            clean_cell = clean_text_for_pdf(cell)
                            row_paragraphs.append(Paragraph(clean_cell, body_style))
                    table_data.append(row_paragraphs)
                i += 1
            
            if table_data and len(table_data) > 1:  # Need at least header + 1 row
                # Create table with proper column widths for letter size (8.5" wide)
                # Account for margins: 8.5" - 1.5" (left+right margins) = 7" usable width
                col_widths = [1.5*inch, 5*inch]  # Category: 1.5", Summary: 5"
                
                table = Table(table_data, hAlign='LEFT', colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2451')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('TOPPADDING', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
            
            in_table = False
            continue
        
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
    """Initialize all session state variables for chat interface."""
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}  # {session_id: {...}}
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # Current chat messages
    if 'awaiting_conflict_resolution' not in st.session_state:
        st.session_state.awaiting_conflict_resolution = False
    if 'conflict_question' not in st.session_state:
        st.session_state.conflict_question = ""
    if 'agent_state' not in st.session_state:
        st.session_state.agent_state = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False

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
