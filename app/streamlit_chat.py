import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import AgentState, create_research_graph
from datetime import datetime
import uuid
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="StratifyAI - AI Research Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - CHAT INTERFACE
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0d1117;
}

/* Hide elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1c1c1c;
    border-right: 1px solid #2d2d2d;
}

/* Chat message */
.user-message {
    background: #10a37f;
    color: white;
    padding: 12px 16px;
    border-radius: 16px;
    border-bottom-right-radius: 4px;
    margin: 8px 0;
    max-width: 75%;
    margin-left: auto;
}

.assistant-message {
    background: #2d2d2d;
    color: #e8e8e8;
    padding: 12px 16px;
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    margin: 8px 0;
    max-width: 75%;
}

.system-message {
    background: #3d3d3d;
    color: #a8a8a8;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px auto;
    max-width: 60%;
    text-align: center;
    font-style: italic;
    font-size: 0.9rem;
}

/* Input */
.stChatInput > div {
    background: #2d2d2d;
    border-radius: 24px;
}

.stChatInput input {
    color: #e8e8e8;
}

/* Buttons */
.stButton > button {
    background: #10a37f;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #0d8c6a;
}

/* Text color */
.stMarkdown, p, h1, h2, h3, span, div {
    color: #e8e8e8;
}

code {
    background: #1c1c1c;
    color: #10a37f;
    padding: 2px 6px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent_state' not in st.session_state:
    st.session_state.agent_state = None
if 'awaiting_resolution' not in st.session_state:
    st.session_state.awaiting_resolution = False
if 'conflict_data' not in st.session_state:
    st.session_state.conflict_data = None
if 'last_report' not in st.session_state:
    st.session_state.last_report = None
if 'last_company' not in st.session_state:
    st.session_state.last_company = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # List of {id, company, timestamp, messages}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# ============================================================================
# PDF GENERATION
# ============================================================================

def generate_pdf_from_markdown(markdown_text: str, company_name: str) -> BytesIO:
    """Generate a professional PDF from markdown text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        topMargin=0.75*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    
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
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#10a37f'),
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
    
    story = []
    
    story.append(Paragraph("Account Plan Report", title_style))
    story.append(Paragraph(f"{company_name} | Generated on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    def clean_text(text):
        """Clean text by converting markdown bold to HTML bold and removing problematic HTML"""
        # First, handle markdown bold (**text**)
        parts = text.split('**')
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are bold
                result.append(f'<b>{part}</b>')
            else:
                result.append(part)
        
        cleaned = ''.join(result)
        
        # Remove any remaining HTML tags except <b> and </b>
        cleaned = re.sub(r'<(?!/?b\b)[^>]+>', '', cleaned)
        
        # Escape special XML characters
        cleaned = cleaned.replace('&', '&amp;')
        cleaned = cleaned.replace('<', '&lt;').replace('>', '&gt;')
        # Restore <b> tags
        cleaned = cleaned.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        
        return cleaned
    
    lines = markdown_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue
            
        # Handle tables
        if '|' in line and not line.startswith('|:'):
            table_data = []
            
            while i < len(lines) and '|' in lines[i]:
                row_text = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                if row_text and not lines[i].startswith('|:'):
                    # Wrap each cell in a Paragraph for proper text wrapping
                    row_paragraphs = []
                    for idx, cell in enumerate(row_text):
                        # Clean the cell text - remove HTML tags and handle bold
                        cell_clean = clean_text(cell)
                        # Replace <br> with newlines
                        cell_clean = cell_clean.replace('<br>', '\n').replace('<br/>', '\n')
                        
                        if idx == 0:  # First column (Category) - use bold
                            row_paragraphs.append(Paragraph(f"<b>{cell_clean}</b>", body_style))
                        else:  # Second column (Summary) - regular text with wrapping
                            row_paragraphs.append(Paragraph(cell_clean, body_style))
                    table_data.append(row_paragraphs)
                i += 1
            
            if table_data and len(table_data) > 1:  # Need at least header + 1 row
                # Create table with proper column widths
                col_widths = [1.5*inch, 5*inch]
                
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
            
            continue
            
        if line.startswith('# ') and not line.startswith('## '):
            text = line[2:].strip()
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph(text, heading1_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading2_style))
        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:].strip()
            clean = clean_text(text)
            story.append(Paragraph(f"• {clean}", bullet_style))
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line).strip()
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', text)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                formatted = f'<b>{link_text}</b><br/><font size="8" color="#666666">{link_url}</font>'
                story.append(Paragraph(formatted, bullet_style))
            else:
                clean = clean_text(text)
                story.append(Paragraph(clean, bullet_style))
        else:
            clean = clean_text(line)
            story.append(Paragraph(clean, body_style))
        
        i += 1
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_message(role, content):
    """Add a message to the chat"""
    st.session_state.messages.append({"role": role, "content": content})
    save_current_chat()

def save_current_chat():
    """Save the current chat to history"""
    if st.session_state.last_company and st.session_state.messages:
        # Check if this chat already exists
        chat_id = st.session_state.current_chat_id
        if chat_id is None:
            chat_id = str(uuid.uuid4())
            st.session_state.current_chat_id = chat_id
        
        # Update or create chat entry
        existing = next((c for c in st.session_state.chat_history if c['id'] == chat_id), None)
        if existing:
            existing['messages'] = st.session_state.messages.copy()
            existing['report'] = st.session_state.last_report
        else:
            st.session_state.chat_history.insert(0, {
                'id': chat_id,
                'company': st.session_state.last_company,
                'timestamp': datetime.now().strftime('%I:%M %p'),
                'messages': st.session_state.messages.copy(),
                'report': st.session_state.last_report
            })

def load_chat(chat_id):
    """Load a chat from history"""
    chat = next((c for c in st.session_state.chat_history if c['id'] == chat_id), None)
    if chat:
        st.session_state.messages = chat['messages'].copy()
        st.session_state.last_company = chat['company']
        st.session_state.last_report = chat.get('report')
        st.session_state.current_chat_id = chat_id
        st.session_state.awaiting_resolution = False

def process_research(company_name):
    """Run the research agent"""
    
    # Start a new chat session
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.last_company = company_name
    
    try:
        # Show processing indicator
        with st.spinner(f"🔍 Researching {company_name}..."):
            initial_state = {
                "messages": [],
                "company_name": company_name,
                "research_data": [],
                "conflicting_info": False,
                "clarification_question": "",
                "conflicting_data": "",
                "final_report": "",
                "human_resolution": ""
            }
            
            graph = create_research_graph()
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            
            result = graph.invoke(initial_state, config)
            
            st.session_state.agent_state = result
            
            # Check for conflict
            if result.get("conflicting_info"):
                st.session_state.awaiting_resolution = True
                st.session_state.conflict_data = {
                    "question": result.get("clarification_question", "Conflict detected"),
                    "config": config
                }
                add_message("assistant", f"⚠️ **Conflict Detected**\n\n{result['clarification_question']}\n\nHow would you like to proceed?")
            else:
                # Success
                report = result.get("final_report", "")
                if report:
                    st.session_state.last_report = report
                    st.session_state.last_company = company_name
                    add_message("assistant", f"✅ **Research Complete!**\n\n{report}")
                else:
                    add_message("assistant", "⚠️ Research completed but no report was generated.")
                    
    except Exception as e:
        add_message("assistant", f"❌ Error: {str(e)}")

def resolve_conflict(choice):
    """Handle conflict resolution"""
    if not st.session_state.agent_state:
        return
    
    current_state = st.session_state.agent_state.copy()
    
    if choice == "proceed":
        add_message("user", "Proceed anyway")
        
        with st.spinner("✍️ Writing report..."):
            current_state["human_resolution"] = "proceed"
            current_state["conflicting_info"] = False
            
            try:
                from src.graph import writer_node
                final_state = writer_node(current_state)
                report = final_state.get("final_report", "")
                
                if report:
                    add_message("assistant", f"✅ **Research Complete!**\n\n{report}")
                else:
                    add_message("assistant", "⚠️ Report generation completed but no output received.")
                    
                st.session_state.awaiting_resolution = False
                st.session_state.agent_state = final_state
                
            except Exception as e:
                add_message("assistant", f"❌ Error: {str(e)}")
        
    elif choice == "stop":
        add_message("user", "Stop for review")
        add_message("assistant", "⏸️ Stopped for manual review. You can start a new research anytime.")
        st.session_state.awaiting_resolution = False
        return
    else:
        # Custom clarification
        add_message("user", choice)
        
        with st.spinner("✍️ Processing your clarification..."):
            current_state["human_resolution"] = "clarification"
            current_state["conflicting_info"] = False
            current_state["research_data"].append({
                "query": "Human Input",
                "content": choice,
                "title": "Clarification",
                "url": "user-input",
                "score": 1.0
            })
            
            try:
                from src.graph import writer_node
                final_state = writer_node(current_state)
                report = final_state.get("final_report", "")
                
                if report:
                    st.session_state.last_report = report
                    st.session_state.last_company = st.session_state.agent_state.get('company_name', 'Company')
                    add_message("assistant", f"✅ **Research Complete!**\n\n{report}")
                else:
                    add_message("assistant", "⚠️ Report generation completed but no output received.")
                    
                st.session_state.awaiting_resolution = False
                st.session_state.agent_state = final_state
                
            except Exception as e:
                add_message("assistant", f"❌ Error: {str(e)}")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🧠 StratifyAI")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_state = None
        st.session_state.awaiting_resolution = False
        st.session_state.last_report = None
        st.session_state.last_company = None
        st.session_state.current_chat_id = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Chat History")
    
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            is_active = chat['id'] == st.session_state.current_chat_id
            button_label = f"{'🟢' if is_active else '💬'} {chat['company']}"
            
            if st.button(button_label, key=f"chat_{chat['id']}", use_container_width=True):
                load_chat(chat['id'])
                st.rerun()
            
            st.caption(chat['timestamp'])
    else:
        st.markdown("*No previous chats*")

# ============================================================================
# MAIN CHAT
# ============================================================================

# Display messages
if len(st.session_state.messages) == 0:
    # Welcome screen - only show when no messages
    st.markdown("""
    <div style='text-align: center; padding: 4rem 1rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>How can I help you today?</h1>
        <p style='color: #a8a8a8; font-size: 1.1rem;'>Ask me to research any company for account planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example prompts
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Research Tesla", use_container_width=True):
            process_research("Tesla")
            st.rerun()
    with col2:
        if st.button("🏢 Research Microsoft", use_container_width=True):
            process_research("Microsoft")
            st.rerun()
else:
    # Show messages when chat has started
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        elif msg["role"] == "system":
            st.markdown(f"<div class='system-message'>{msg['content']}</div>", unsafe_allow_html=True)

# Conflict resolution UI
if st.session_state.awaiting_resolution:
    st.markdown("---")
    st.markdown("### Choose an option:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ 1. Proceed", use_container_width=True):
            resolve_conflict("proceed")
            st.rerun()
    
    with col2:
        if st.button("🛑 2. Stop", use_container_width=True):
            resolve_conflict("stop")
            st.rerun()
    
    with col3:
        st.markdown("*or type below*")
    
    clarification = st.text_input("3. Provide clarification:", key="clarification_input")
    if clarification:
        resolve_conflict(clarification)
        st.rerun()

# Download section - show if report is available and NOT waiting for conflict resolution
if st.session_state.last_report and not st.session_state.awaiting_resolution:
    st.markdown("---")
    st.markdown("### 📥 Download Report")
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        st.download_button(
            label="📥 Download Markdown",
            data=st.session_state.last_report,
            file_name=f"account_plan_{st.session_state.last_company.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_md"
        )
    
    with col2:
        try:
            pdf_buffer = generate_pdf_from_markdown(
                st.session_state.last_report,
                st.session_state.last_company
            )
            
            st.download_button(
                label="📄 Download PDF",
                data=pdf_buffer,
                file_name=f"account_plan_{st.session_state.last_company.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf"
            )
        except Exception as e:
            st.error(f"PDF error: {str(e)}")

# Chat input - always at the bottom
if not st.session_state.awaiting_resolution:
    user_input = st.chat_input("Type a company name to research...")
    
    if user_input:
        add_message("user", user_input)
        process_research(user_input)
        st.rerun()
