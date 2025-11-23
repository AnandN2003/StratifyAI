from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
from src.graph import AgentState, create_research_graph
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import re
import json
import time

app = Flask(__name__)
CORS(app)

# Store active sessions
active_sessions = {}

@app.route('/api/research', methods=['POST'])
def research_company():
    try:
        data = request.json
        user_input = data.get('company_name')
        
        if not user_input:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Extract actual company name from natural language input using LLM
        from src.graph import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        print(f"📥 User input: {user_input}")
        
        extraction_prompt = SystemMessage(content="""You are a company name extractor. 
Extract ONLY the company name from the user's input. Return just the company name, nothing else.

Examples:
- "I want to research about a company called AstraZeneca" -> "AstraZeneca"
- "Can you analyze Tesla for me?" -> "Tesla"
- "Research Microsoft" -> "Microsoft"
- "Tell me about Apple Inc" -> "Apple"
- "accenture" -> "Accenture"

Return ONLY the company name.""")
        
        llm = get_llm()
        response = llm.invoke([extraction_prompt, HumanMessage(content=user_input)])
        company_name = response.content.strip()
        
        print(f"✅ Extracted company name: {company_name}")
        
        def generate():
            """Generator function for streaming progress updates"""
            try:
                # Send initial status
                yield f"data: {json.dumps({'type': 'progress', 'message': f'🔍 Starting research for {company_name}...'})}\n\n"
                time.sleep(0.5)
                
                # Initialize state
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
                
                # Create graph and run
                graph = create_research_graph()
                thread_id = f"session_{company_name}_{id(graph)}"
                config = {"configurable": {"thread_id": thread_id}}
                
                # Store in active sessions
                active_sessions[company_name] = {
                    "graph": graph,
                    "thread_id": thread_id,
                    "config": config
                }
                
                yield f"data: {json.dumps({'type': 'progress', 'message': '📊 Gathering company data from multiple sources...'})}\n\n"
                time.sleep(0.5)
                
                # Run the graph with progress tracking
                result_state = None
                last_node = None
                
                for state in graph.stream(initial_state, config, stream_mode="values"):
                    result_state = state
                    
                    # Detect which node we're in based on state changes
                    if state.get('research_data') and not last_node:
                        last_node = 'researcher'
                        yield f"data: {json.dumps({'type': 'progress', 'message': '✅ Research data collected - analyzing for conflicts...'})}\n\n"
                        time.sleep(0.5)
                    elif state.get('conflicting_info') and last_node == 'researcher':
                        last_node = 'reviewer'
                        yield f"data: {json.dumps({'type': 'progress', 'message': '⚠️ Conflict detected - pausing for review...'})}\n\n"
                        time.sleep(0.5)
                    elif state.get('final_report') and not state.get('conflicting_info'):
                        last_node = 'writer'
                        yield f"data: {json.dumps({'type': 'progress', 'message': '📝 Generating comprehensive account plan...'})}\n\n"
                        time.sleep(0.5)
                
                # Check if we hit an interrupt (conflict detected)
                if result_state.get("conflicting_info"):
                    yield f"data: {json.dumps({'type': 'conflict', 'conflict_question': result_state.get('clarification_question', ''), 'conflicting_data': result_state.get('conflicting_data', ''), 'session_id': company_name})}\n\n"
                else:
                    # No conflict - return the report
                    report = result_state.get('final_report', '')
                    yield f"data: {json.dumps({'type': 'complete', 'report': report})}\n\n"
                
            except Exception as e:
                import traceback
                print("Error in generate():")
                print(traceback.format_exc())
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        import traceback
        print("Error in research_company:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/resolve-conflict', methods=['POST'])
def resolve_conflict():
    try:
        data = request.json
        print(f"\n{'='*60}")
        print(f"🔍 RESOLVE CONFLICT REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"📦 Request data: {data}")
        
        resolution = data.get('resolution')
        session_id = data.get('session_id')
        clarification_note = data.get('clarification_note', '')
        
        print(f"✅ Resolution: {resolution}")
        print(f"✅ Session ID: {session_id}")
        print(f"✅ Clarification note: {clarification_note}")
        print(f"📋 Active sessions: {list(active_sessions.keys())}")
        print(f"{'='*60}\n")
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
            
        if session_id not in active_sessions:
            return jsonify({'error': f'Session not found. Active sessions: {list(active_sessions.keys())}'}), 400
        
        company_name = session_id
        session = active_sessions[company_name]
        graph = session['graph']
        config = session['config']
        
        # Update state with human resolution
        if resolution == 'proceed':
            updated_state = {
                "conflicting_info": False,
                "human_resolution": "proceed"
            }
        elif resolution == 'stop':
            # Clean up session
            del active_sessions[company_name]
            return jsonify({
                'status': 'stopped',
                'message': 'Research stopped by user',
                'report': '# Research Paused\n\nResearch was stopped due to conflicting information requiring manual review.'
            })
        elif resolution == 'clarify':
            updated_state = {
                "conflicting_info": False,
                "human_resolution": f"clarify: {clarification_note}"
            }
        else:
            return jsonify({'error': 'Invalid resolution type'}), 400
        
        # Continue the graph from where it paused
        print(f"🔄 Resuming graph execution...")
        print(f"📝 Updating state and resuming...")
        
        # Update the graph state at the current checkpoint
        graph.update_state(config, updated_state, as_node="human_review")
        
        # Resume execution from the updated state
        result_state = None
        for state in graph.stream(None, config, stream_mode="values"):
            result_state = state
            print(f"📊 Graph state update: conflicting_info={state.get('conflicting_info')}, has_report={bool(state.get('final_report'))}")
            if state.get('final_report'):
                print(f"✅ Report generated in stream!")
                break
        
        report = result_state.get('final_report', '')
        print(f"\n{'='*60}")
        print(f"✅ GRAPH EXECUTION COMPLETED")
        print(f"📄 Report length: {len(report)} characters")
        if report:
            print(f"📄 Report preview: {report[:150]}...")
        else:
            print(f"⚠️ WARNING: No report generated!")
        print(f"{'='*60}\n")
        
        # Clean up session
        del active_sessions[company_name]
        
        return jsonify({
            'status': 'completed',
            'message': 'Research completed with human resolution',
            'report': report
        })
        
    except Exception as e:
        import traceback
        print("Error in resolve_conflict:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        content = data.get('content', '')
        company_name = data.get('company_name', 'Report')
        
        print(f"📄 PDF generation request for: {company_name}")
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=60, 
            leftMargin=60,
            topMargin=60, 
            bottomMargin=40,
            title=f"{company_name} Account Plan"
        )
        
        # Container for PDF elements
        elements = []
        
        # Define professional styles
        styles = getSampleStyleSheet()
        
        # Title style (company name)
        title_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#ff4444'),
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Section heading style (## headers)
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#ff4444'),
            borderWidth=0,
            borderPadding=0,
            leftIndent=0
        )
        
        # Subsection style (### headers)
        subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#444444'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=0,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        )
        
        # Bullet point style
        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leftIndent=20,
            fontName='Helvetica',
            leading=13
        )
        
        # Parse markdown content
        lines = content.split('\n')
        i = 0
        in_table = False
        table_data = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                if not in_table:
                    elements.append(Spacer(1, 0.15 * inch))
                i += 1
                continue
            
            # Handle main title (# header - company name)
            if line.startswith('# ') and i < 3:  # Main title at the top
                text = line.replace('# ', '').replace('Account Plan:', '').strip()
                elements.append(Paragraph(text, title_style))
                elements.append(Paragraph('Account Plan & Strategic Analysis', subtitle_style))
                elements.append(Spacer(1, 0.3 * inch))
                i += 1
                continue
            
            # Handle section headers (## )
            elif line.startswith('## '):
                text = line.replace('## ', '')
                # Add section divider line
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(text, section_style))
                # Add underline
                elements.append(Spacer(1, 0.05 * inch))
                i += 1
                continue
            
            # Handle subsection headers (###)
            elif line.startswith('### '):
                text = line.replace('### ', '')
                elements.append(Paragraph(text, subsection_style))
                i += 1
                continue
            
            # Handle table rows
            elif line.startswith('|'):
                if not in_table:
                    in_table = True
                    table_data = []
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                
                # Skip separator rows (----)
                if all('-' in cell for cell in cells):
                    i += 1
                    continue
                
                # Clean up cell content - remove markdown formatting
                cleaned_cells = []
                for cell in cells:
                    # Remove ** for bold
                    cell = cell.replace('**', '')
                    # Replace <br> with line breaks
                    cell = cell.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
                    # Replace - bullet points with actual bullets
                    cell = re.sub(r'^\s*-\s+', '• ', cell)
                    # Clean up multiple spaces
                    cell = re.sub(r'\s+', ' ', cell)
                    cleaned_cells.append(cell)
                
                table_data.append(cleaned_cells)
                i += 1
                
                # Check if next line is still part of table
                if i < len(lines) and not lines[i].strip().startswith('|'):
                    # End of table - render it
                    if table_data:
                        # Convert table cells to Paragraph objects for better text wrapping
                        wrapped_table_data = []
                        for row_idx, row in enumerate(table_data):
                            wrapped_row = []
                            for col_idx, cell in enumerate(row):
                                if row_idx == 0:
                                    # Header row - keep as plain text
                                    wrapped_row.append(cell)
                                else:
                                    # Body rows - wrap in Paragraph for automatic line breaking
                                    para = Paragraph(cell, bullet_style)
                                    wrapped_row.append(para)
                            wrapped_table_data.append(wrapped_row)
                        
                        # Create table with appropriate column widths (total width = 6.5")
                        table = Table(wrapped_table_data, colWidths=[1.3*inch, 5.2*inch])
                        table.setStyle(TableStyle([
                            # Header row styling
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff4444')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('TOPPADDING', (0, 0), (-1, 0), 12),
                            
                            # Body rows styling
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 8),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                            ('TOPPADDING', (0, 1), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                            
                            # Grid
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#ff4444')),
                            
                            # Alternating row colors
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 0.2 * inch))
                        table_data = []
                    in_table = False
                continue
            
            # Handle bold bullet points (• **text:** content)
            elif line.startswith('* **') or line.startswith('- **'):
                in_table = False
                text = line.replace('* ', '').replace('- ', '')
                # Remove ** for bold and use <b> tags
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Remove any remaining <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(f"• {text}", bullet_style))
                i += 1
                continue
            
            # Handle regular bullet points
            elif line.startswith('* ') or line.startswith('- ') or re.match(r'^\d+\.', line):
                in_table = False
                text = re.sub(r'^[\*\-]\s+', '', line)
                text = re.sub(r'^\d+\.\s+', '', text)
                # Convert **bold** to <b>bold</b>
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                # Remove any <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(f"• {text}", bullet_style))
                i += 1
                continue
            
            # Handle regular paragraphs
            else:
                in_table = False
                # Convert **bold** to <b>bold</b>
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Convert *italic* to <i>italic</i>
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                # Remove any <br> tags
                text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
                elements.append(Paragraph(text, body_style))
                i += 1
                continue
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        print(f"✅ PDF generated successfully: {len(buffer.getvalue())} bytes")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{company_name}_account_plan.pdf'
        )
        
    except Exception as e:
        import traceback
        print("Error generating PDF:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-section', methods=['POST'])
def edit_section():
    try:
        data = request.json
        company_name = data.get('company_name', 'report')
        edit_instructions = data.get('edit_instructions')
        full_report = data.get('full_report')
        
        print(f"📝 Report edit request:")
        print(f"  Company: {company_name}")
        print(f"  Instructions: {edit_instructions}")
        
        if not edit_instructions or not full_report:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use Gemini to update the report based on instructions
        from src.graph import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        system_prompt = """You are an expert Sales Strategist updating an account plan based on user feedback.

Your task:
1. Read the current account plan carefully
2. Apply the user's editing instructions to improve the report
3. Return the COMPLETE updated report in markdown format
4. Maintain the same structure and section headers
5. Keep the professional style and formatting
6. Only modify the parts requested by the user, keep everything else intact

IMPORTANT: Return the FULL report with all sections, not just the changed parts."""

        user_prompt = f"""Current Account Plan:

{full_report}

---

User's editing instructions:
{edit_instructions}

Please update the account plan following these instructions and return the complete updated report."""

        print(f"  → Sending to Gemini for report update...")
        
        llm = get_llm()
        llm_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(llm_messages)
        updated_report = response.content.strip()
        
        # Clean up markdown code blocks if present
        if "```markdown" in updated_report:
            updated_report = updated_report.split("```markdown")[1].split("```")[0].strip()
        elif "```" in updated_report:
            updated_report = updated_report.replace("```", "").strip()
        
        print(f"  ✓ Report updated ({len(updated_report)} characters)")
        print(f"✅ Report regenerated successfully with AI")
        
        return jsonify({
            'status': 'success',
            'message': 'Report updated based on your instructions',
            'updated_report': updated_report
        })
        
    except Exception as e:
        import traceback
        print("Error in edit_section:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
